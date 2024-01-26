import asyncio

import streamlit as st
from webui_pages.utils import *
from streamlit_chatbox import *
from streamlit_modal import Modal
from datetime import datetime
import os
import re
import time
from configs import (
    TEMPERATURE,
    HISTORY_LEN,
    PROMPT_TEMPLATES,
    DEFAULT_KNOWLEDGE_BASE,
    DEFAULT_SEARCH_ENGINE,
    SUPPORT_AGENT_MODEL, KNOWLEDGE_USE_CACHE)
from server.knowledge_base.utils import LOADER_DICT
import uuid
from typing import List, Dict

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "img",
        "chatchat_icon_blue_square_v2.png"
    )
)


def get_messages_history(
        history_len: int,
        content_in_expander: bool = False) -> List[Dict]:
    '''
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    '''

    def filter(msg):
        content = [x for x in msg["elements"]
                   if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)


@st.cache_data
def upload_temp_docs(files, _api: ApiRequest) -> str:
    '''
    将文件上传到临时目录，用于文件对话
    返回临时向量库ID
    '''
    return _api.upload_temp_docs(files).get("data", {}).get("id")


def parse_command(text: str, modal: Modal) -> bool:
    '''
    检查用户是否输入了自定义命令，当前支持：
    /new {session_name}。如果未提供名称，默认为“会话X”
    /del {session_name}。如果未提供名称，在会话数量>1的情况下，删除当前会话。
    /clear {session_name}。如果未提供名称，默认清除当前会话
    /help。查看命令帮助
    返回值：输入的是命令返回True，否则返回False
    '''
    if m := re.match(r"/([^\s]+)\s*(.*)", text):
        cmd, name = m.groups()
        name = name.strip()
        conv_names = chat_box.get_chat_names()
        if cmd == "help":
            modal.open()
        elif cmd == "new":
            if not name:
                i = 1
                while True:
                    name = f"Session{i}"
                    if name not in conv_names:
                        break
                    i += 1
            if name in st.session_state["conversation_ids"]:
                st.error(f"Session Name “{name}” exists")
                time.sleep(1)
            else:
                st.session_state["conversation_ids"][name] = uuid.uuid4().hex
                st.session_state["cur_conv_name"] = name
        elif cmd == "del":
            name = name or st.session_state.get("cur_conv_name")
            if len(conv_names) == 1:
                st.error("This is the last session and cannot be deleted")
                time.sleep(1)
            elif not name or name not in st.session_state["conversation_ids"]:
                st.error(f"Invalid session name:“{name}”")
                time.sleep(1)
            else:
                st.session_state["conversation_ids"].pop(name, None)
                chat_box.del_chat_name(name)
                st.session_state["cur_conv_name"] = ""
        elif cmd == "clear":
            chat_box.reset_history(name=name or None)
        return True
    return False


def dialogue_page(api: ApiRequest, is_lite: bool = False):
    st.session_state.setdefault("conversation_ids", {})
    st.session_state["conversation_ids"].setdefault(
        chat_box.cur_chat_name, uuid.uuid4().hex)
    st.session_state.setdefault("file_chat_id", None)
    default_model = api.get_default_llm_model()[0]

    if "ignore_cache" not in st.session_state:
        st.session_state.ignore_cache = False

    if "show_ignore_cache_button" not in st.session_state:
        st.session_state.show_ignore_cache_button = False

    if "cache_prompt" not in st.session_state:
        st.session_state.cache_prompt = False

    if not chat_box.chat_inited:
        chat_box.init_session()

    # 弹出自定义命令帮助信息
    modal = Modal("自定义命令", key="cmd_help", max_width="500")
    if modal.is_open():
        with modal.container():
            cmds = [x for x in parse_command.__doc__.split(
                "\n") if x.strip().startswith("/")]
            st.write("\n\n".join(cmds))

    with st.sidebar:
        # 多会话
        conversation_name = 'default'
        chat_box.use_chat_name(conversation_name)
        conversation_id = st.session_state["conversation_ids"][conversation_name]

        # TODO: 对话模型与会话绑定
        def on_mode_change():
            mode = st.session_state.dialogue_mode
            text = f"Switch to {mode} mode"
            if mode == "knowledge_base_chat":
                cur_kb = st.session_state.get("selected_kb")
                if cur_kb:
                    text = f"{text} Current Knowledge base： `{cur_kb}`。"
            st.toast(text)

        dialogue_modes = ["llm_chat",
                          "knowledge_base_chat"
                          ]
        dialogue_mode = st.selectbox("Please select chat mode：",
                                     dialogue_modes,
                                     index=0,
                                     on_change=on_mode_change,
                                     key="dialogue_mode",
                                     )

        def on_llm_change():
            if llm_model:
                config = api.get_model_config(llm_model)
                if not config.get("online_api"):  # 只有本地model_worker可以切换模型
                    st.session_state["prev_llm_model"] = llm_model
                st.session_state["cur_llm_model"] = st.session_state.llm_model

        def llm_model_format_func(x):
            if x in running_models:
                return f"{x} (Running)"
            return x

        running_models = list(api.list_running_models())
        available_models = []
        config_models = api.list_config_models()
        if not is_lite:
            for k, v in config_models.get(
                    "local", {}).items():  # 列出配置了有效本地路径的模型
                if (v.get("model_path_exists")
                        and k not in running_models):
                    available_models.append(k)
        for k, v in config_models.get(
                "online", {}).items():  # 列出ONLINE_MODELS中直接访问的模型
            if not v.get("provider") and k not in running_models:
                available_models.append(k)
        llm_models = running_models + available_models
        cur_llm_model = st.session_state.get("cur_llm_model", default_model)
        if cur_llm_model in llm_models:
            index = llm_models.index(cur_llm_model)
        else:
            index = 0
        llm_model = st.selectbox("Choose LLM Model：",
                                 llm_models,
                                 index,
                                 format_func=llm_model_format_func,
                                 on_change=on_llm_change,
                                 key="llm_model",
                                 )
        if (st.session_state.get("prev_llm_model") != llm_model
                and not is_lite
                and llm_model not in config_models.get("online", {})
                and llm_model not in config_models.get("langchain", {})
                and llm_model not in running_models):
            with st.spinner(f"Loading Model： {llm_model}，Do not perform operations or refresh the page"):
                prev_model = st.session_state.get("prev_llm_model")
                r = api.change_llm_model(prev_model, llm_model)
                if msg := check_error_msg(r):
                    st.error(msg)
                elif msg := check_success_msg(r):
                    st.success(msg)
                    st.session_state["prev_llm_model"] = llm_model

        index_prompt = {
            "llm_chat": "llm_chat",
            "agent_chat": "agent_chat",
            "search_engine_chat": "search_engine_chat",
            "knowledge_base_chat": "knowledge_base_chat",
            "file_chat": "knowledge_base_chat"
        }
        prompt_templates_kb_list = list(PROMPT_TEMPLATES[index_prompt[dialogue_mode]].keys())
        prompt_template_name = prompt_templates_kb_list[0]
        # if "prompt_template_select" not in st.session_state:
        #     st.session_state.prompt_template_select = prompt_templates_kb_list[0]

        # def prompt_change():
        #     text = f"已切换为 {prompt_template_name} 模板。"
        #     st.toast(text)

        # prompt_template_select = st.selectbox(
        #     "请选择Prompt模板：",
        #     prompt_templates_kb_list,
        #     index=0,
        #     on_change=prompt_change,
        #     key="prompt_template_select",
        # )

        def on_kb_change():
            st.toast(f"Loaded Knowledge bases： {st.session_state.selected_kb}")

        if dialogue_mode == "knowledge_base_chat":
            with st.expander("knowledge_base_setting", True):
                kb_list = api.list_knowledge_bases()
                index = 0
                if DEFAULT_KNOWLEDGE_BASE in kb_list:
                    index = kb_list.index(DEFAULT_KNOWLEDGE_BASE)
                selected_kb = st.selectbox(
                    "Please choose knowledge base：",
                    kb_list,
                    index=index,
                    on_change=on_kb_change,
                    key="selected_kb",
                )
                kb_top_k = st.number_input("Matched Chunk Num：", 1, 20, VECTOR_SEARCH_TOP_K)

                ## Bge 模型会超过1
                score_threshold = st.slider("Knowledge matching score threshold：", 0.0, 2.0, float(SCORE_THRESHOLD), 0.01)

        elif dialogue_mode == "file_chat":
            with st.expander("文件对话配置", True):
                files = st.file_uploader(
                    "上传知识文件：", [
                        i for ls in LOADER_DICT.values() for i in ls], accept_multiple_files=True, )
                kb_top_k = st.number_input(
                    "匹配知识条数：", 1, 20, VECTOR_SEARCH_TOP_K)

                # Bge 模型会超过1
                score_threshold = st.slider(
                    "知识匹配分数阈值：", 0.0, 2.0, float(SCORE_THRESHOLD), 0.01)
                if st.button("开始上传", disabled=len(files) == 0):
                    st.session_state["file_chat_id"] = upload_temp_docs(
                        files, api)
        elif dialogue_mode == "表格数据问答":
            print("表格数据问答")
        elif dialogue_mode == "搜索引擎问答":
            search_engine_list = api.list_search_engines()
            if DEFAULT_SEARCH_ENGINE in search_engine_list:
                index = search_engine_list.index(DEFAULT_SEARCH_ENGINE)
            else:
                index = search_engine_list.index(
                    "duckduckgo") if "duckduckgo" in search_engine_list else 0
            with st.expander("搜索引擎配置", True):
                search_engine = st.selectbox(
                    label="请选择搜索引擎",
                    options=search_engine_list,
                    index=index,
                )
                se_top_k = st.number_input(
                    "匹配搜索结果条数：", 1, 20, SEARCH_ENGINE_TOP_K)


    # Display chat messages from history on app rerun
    chat_box.output_messages()

    chat_input_placeholder = "Please enter the conversation content and use Shift+Enter for line breaks. Enter /help to view custom commands "

    def on_feedback(
            feedback,
            message_id: str = "",
            history_index: int = -1,
    ):
        reason = feedback["text"]
        score_int = chat_box.set_feedback(
            feedback=feedback, history_index=history_index)
        api.chat_feedback(message_id=message_id,
                          score=score_int,
                          reason=reason)
        st.session_state["need_rerun"] = True

    feedback_kwargs = {
        "feedback_type": "thumbs",
        "optional_text_label": "欢迎反馈您打分的理由",
    }

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        history = get_messages_history(HISTORY_LEN)
        chat_box.user_say(prompt)
        st.session_state.cache_prompt = prompt
        if dialogue_mode == "llm_chat":
            chat_box.ai_say("LLM Thinking...")
            text = ""
            message_id = ""
            r = api.chat_chat(prompt,
                              history=history,
                              conversation_id=conversation_id,
                              model=llm_model,
                              prompt_name=prompt_template_name,
                              temperature=TEMPERATURE)
            for t in r:
                if error_msg := check_error_msg(
                        t):  # check whether error occured
                    st.error(error_msg)
                    break
                text += t.get("text", "")
                chat_box.update_msg(text)
                message_id = t.get("message_id", "")

            metadata = {
                "message_id": message_id,
            }
            chat_box.update_msg(
                text, streaming=False, metadata=metadata)  # 更新最终的字符串，去除光标
            chat_box.show_feedback(
                **feedback_kwargs,
                key=message_id,
                on_submit=on_feedback,
                kwargs={
                    "message_id": message_id,
                    "history_index": len(
                        chat_box.history) - 1})
        elif dialogue_mode == "自定义Agent问答":
            if not any(
                    agent in llm_model for agent in SUPPORT_AGENT_MODEL):
                chat_box.ai_say([
                    f"正在思考... \n\n <span style='color:red'>该模型并没有进行Agent对齐，请更换支持Agent的模型获得更好的体验！</span>\n\n\n",
                    Markdown("...", in_expander=True, title="思考过程", state="complete"),

                ])
            else:
                chat_box.ai_say([f"正在思考...", Markdown(
                    "...", in_expander=True, title="思考过程", state="complete"), ])
            text = ""
            ans = ""
            for d in api.agent_chat(prompt,
                                    history=history,
                                    model=llm_model,
                                    prompt_name=prompt_template_name,
                                    temperature=TEMPERATURE,
                                    ):
                try:
                    d = json.loads(d)
                except BaseException:
                    pass
                if error_msg := check_error_msg(
                        d):  # check whether error occured
                    st.error(error_msg)
                if chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=1)
                if chunk := d.get("final_answer"):
                    ans += chunk
                    chat_box.update_msg(ans, element_index=0)
                if chunk := d.get("tools"):
                    text += "\n\n".join(d.get("tools", []))
                    chat_box.update_msg(text, element_index=1)
            chat_box.update_msg(ans, element_index=0, streaming=False)
            chat_box.update_msg(text, element_index=1, streaming=False)
        elif dialogue_mode == "knowledge_base_chat":
            if not KNOWLEDGE_USE_CACHE:
                # 不带缓存的逻辑
                chat_box.ai_say([f"正在查询知识库 `{selected_kb}` ...", Markdown(
                    "...", in_expander=True, title="知识库匹配结果", state="complete"), ])
                doc_text = ""
                chat_box.update_msg(
                    f"正在查询知识库 `{selected_kb}` ...",
                    element_index=0,
                    streaming=False)
                chat_box.update_msg(
                    "", element_index=1, streaming=False, title="知识库匹配结果")
                for d in api.knowledge_base_chat(
                        prompt,
                        knowledge_base_name=selected_kb,
                        top_k=kb_top_k,
                        score_threshold=score_threshold,
                        history=history,
                        ignore_cache=True,
                        model=llm_model,
                        prompt_name=prompt_template_name,
                        temperature=TEMPERATURE):
                    if error_msg := check_error_msg(
                            d):  # check whether error occured
                        st.error(error_msg)
                    elif chunk := d.get("answer"):
                        doc_text += chunk
                        chat_box.update_msg(doc_text, element_index=0)
                chat_box.update_msg(
                    doc_text, element_index=0, streaming=False)
                chat_box.update_msg(
                    "\n\n".join(
                        d.get(
                            "docs",
                            [])),
                    element_index=1,
                    streaming=False,
                    title="知识库匹配结果")
            else:
                # 带缓存的逻辑
                chat_box.ai_say([f"查询缓存中...", Markdown(
                    "...", in_expander=True, title="缓存匹配结果", state="complete"), ])
                text = ""
                for d in api.knowledge_base_chat(
                        prompt,
                        knowledge_base_name=selected_kb,
                        top_k=kb_top_k,
                        score_threshold=score_threshold,
                        history=history,
                        ignore_cache=False,
                        model=llm_model,
                        prompt_name=prompt_template_name,
                        temperature=TEMPERATURE):
                    if error_msg := check_error_msg(
                            d):  # check whether error occured
                        st.error(error_msg)
                    elif chunk := d.get("answer"):
                        text += chunk
                if text == "No Cache":
                    st.session_state.show_ignore_cache_button = False
                    doc_text = ""
                    chat_box.update_msg(
                        f"正在查询知识库 `{selected_kb}` ...",
                        element_index=0,
                        streaming=False)
                    chat_box.update_msg(
                        "", element_index=1, streaming=False, title="知识库匹配结果")
                    for d in api.knowledge_base_chat(
                            prompt,
                            knowledge_base_name=selected_kb,
                            top_k=kb_top_k,
                            score_threshold=score_threshold,
                            history=history,
                            ignore_cache=True,
                            model=llm_model,
                            prompt_name=prompt_template_name,
                            temperature=TEMPERATURE):
                        if error_msg := check_error_msg(
                                d):  # check whether error occured
                            st.error(error_msg)
                        elif chunk := d.get("answer"):
                            doc_text += chunk
                            chat_box.update_msg(doc_text, element_index=0)
                    chat_box.update_msg(
                        doc_text, element_index=0, streaming=False)
                    chat_box.update_msg(
                        "\n\n".join(
                            d.get(
                                "docs",
                                [])),
                        element_index=1,
                        streaming=False,
                        title="知识库匹配结果")
                else:
                    chat_box.update_msg(
                        '查询缓存结束', element_index=0, streaming=False)
                    doc_text = f"<div style='background-color:#f5f5f5; padding: 5px; border-radius: 5px; margin-bottom: 20px;'><span style='color:#67C23A; margin-bottom: 10px;'>命中的历史问题：</span><br>{text}</div>"
                    chat_box.update_msg(
                        doc_text,
                        element_index=1,
                        streaming=False,
                        expanded=True,
                        title="缓存匹配结果")
                    st.session_state.show_ignore_cache_button = True

        elif dialogue_mode == "文件对话":
            if st.session_state["file_chat_id"] is None:
                st.error("请先上传文件再进行对话")
                st.stop()
            chat_box.ai_say([
                f"正在查询文件 `{st.session_state['file_chat_id']}` ...",
                Markdown("...", in_expander=True, title="文件匹配结果", state="complete"),
            ])
            text = ""
            for d in api.file_chat(
                    prompt,
                    knowledge_id=st.session_state["file_chat_id"],
                    top_k=kb_top_k,
                    score_threshold=score_threshold,
                    history=history,
                    model=llm_model,
                    prompt_name=prompt_template_name,
                    temperature=TEMPERATURE):
                if error_msg := check_error_msg(
                        d):  # check whether error occured
                    st.error(error_msg)
                elif chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            chat_box.update_msg(
                "\n\n".join(
                    d.get(
                        "docs",
                        [])),
                element_index=1,
                streaming=False)
        elif dialogue_mode == "搜索引擎问答":
            chat_box.ai_say([f"正在执行 `{search_engine}` 搜索...", Markdown(
                "...", in_expander=True, title="网络搜索结果", state="complete"), ])
            text = ""
            for d in api.search_engine_chat(
                    prompt,
                    search_engine_name=search_engine,
                    top_k=se_top_k,
                    history=history,
                    model=llm_model,
                    prompt_name=prompt_template_name,
                    temperature=TEMPERATURE,
                    split_result=se_top_k > 1):
                if error_msg := check_error_msg(
                        d):  # check whether error occured
                    st.error(error_msg)
                elif chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            chat_box.update_msg(
                "\n\n".join(
                    d.get(
                        "docs",
                        [])),
                element_index=1,
                streaming=False)

        if st.session_state.get("need_rerun"):
            st.session_state["need_rerun"] = False
            st.rerun()

    if dialogue_mode == "knowledge_base_chat" and st.session_state.show_ignore_cache_button:
        if st.button(
            "缓存有误，重新请求大模型",
            key="ignore_cache_button",
                type="primary"):
            st.session_state.show_ignore_cache_button = False
            history = get_messages_history(HISTORY_LEN)
            chat_box.ai_say([f"正在查询知识库 `{selected_kb}` ...", Markdown(
                "...", in_expander=True, title="知识库匹配结果", state="complete"), ])
            doc_text = ""
            for d in api.knowledge_base_chat(st.session_state.cache_prompt,
                                             knowledge_base_name=selected_kb,
                                             top_k=kb_top_k,
                                             score_threshold=score_threshold,
                                             history=history,
                                             ignore_cache=True,
                                             model=llm_model,
                                             prompt_name=prompt_template_name,
                                             temperature=TEMPERATURE):
                if error_msg := check_error_msg(
                        d):  # check whether error occured
                    st.error(error_msg)
                elif chunk := d.get("answer"):
                    doc_text += chunk
                    chat_box.update_msg(doc_text, element_index=0)
            chat_box.update_msg(doc_text, element_index=0, streaming=False)
            chat_box.update_msg(
                "\n\n".join(
                    d.get(
                        "docs",
                        [])),
                element_index=1,
                streaming=False)
            st.session_state.cache_prompt = ""
            st.rerun()

    now = datetime.now()
    with st.sidebar:

        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )
