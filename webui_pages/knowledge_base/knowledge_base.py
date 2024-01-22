import streamlit as st
from webui_pages.utils import *
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from server.knowledge_base.utils import get_file_path, LOADER_DICT
from server.knowledge_base.kb_service.base import get_kb_details, get_kb_file_details
from typing import Literal, Dict, Tuple
from configs import (EMBEDDING_MODEL, CHUNK_SIZE, OVERLAP_SIZE, ZH_TITLE_ENHANCE)
from server.utils import list_embed_models, list_online_embed_models
import os
import time


# SENTENCE_SIZE = 100

cell_renderer = JsCode("""function(params) {if(params.value==true){return '✓'}else{return '×'}}""")


def config_aggrid(
        df: pd.DataFrame,
        columns: Dict[Tuple[str, str], Dict] = {},
        selection_mode: Literal["single", "multiple", "disabled"] = "single",
        use_checkbox: bool = False,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("No", width=40)
    for (col, header), kw in columns.items():
        gb.configure_column(col, header, wrapHeaderText=True, **kw)
    gb.configure_selection(
        selection_mode=selection_mode,
        use_checkbox=use_checkbox,
        # pre_selected_rows=st.session_state.get("selected_rows", [0]),
    )
    gb.configure_pagination(
        enabled=True,
        paginationAutoPageSize=False,
        paginationPageSize=10
    )
    return gb


def file_exists(kb: str, selected_rows: List) -> Tuple[str, str]:
    """
    check whether a doc file exists in local knowledge base folder.
    return the file's name and path if it exists.
    """
    if selected_rows:
        file_name = selected_rows[0]["file_name"]
        file_path = get_file_path(kb, file_name)
        if os.path.isfile(file_path):
            return file_name, file_path
    return "", ""


def knowledge_base_page(api: ApiRequest, is_lite: bool = None):
    try:
        kb_list = {x["kb_name"]: x for x in get_kb_details()}
    except Exception as e:
        st.error("There is an error in obtaining knowledge base information. Please check whether the initialization or migration has been completed according to the steps of `4 Knowledge Base Initialization and Migration` in `README.md`, or whether there is a database connection error.")
        #st.error("获取知识库信息错误，请检查是否已按照 `README.md` 中 `4 知识库初始化与迁移` 步骤完成初始化或迁移，或是否为数据库连接错误。")
        st.stop()
    kb_names = list(kb_list.keys())

    if "selected_kb_name" in st.session_state and st.session_state["selected_kb_name"] in kb_names:
        selected_kb_index = kb_names.index(st.session_state["selected_kb_name"])
    else:
        selected_kb_index = 0

    if "selected_kb_info" not in st.session_state:
        st.session_state["selected_kb_info"] = ""


    if "selected_splits_info" not in st.session_state:
        st.session_state["selected_splits_info"] = []


    def format_selected_kb(kb_name: str) -> str:
        if kb := kb_list.get(kb_name):
            return f"{kb_name} ({kb['embed_model']})"
        else:
            return kb_name

    selected_kb = st.selectbox(
        "Please select or create a new knowledge base:",
        kb_names + ["Create Knowledge Base"],
        format_func=format_selected_kb,
        index=selected_kb_index
    )

    if selected_kb == "Create Knowledge Base":
        with st.form("Create Knowledge Base"):

            kb_name = st.text_input(
                "New KnowledgeBase Name",
                placeholder="New knowledge base name, Chinese naming is not supported",
                key="kb_name",
            )
            kb_info = st.text_input(
                "Knowledge base introduction",
                placeholder="Introduction to knowledge base to facilitate Agent search",
                key="kb_info",
            )

            cols = st.columns(1)

            if is_lite:
                embed_models = list_online_embed_models()
            else:
                embed_models = list_embed_models() + list_online_embed_models()

            embed_model = cols[0].selectbox(
                "Embedding Model",
                embed_models,
                index=embed_models.index(EMBEDDING_MODEL),
                key="embed_model",
            )

            submit_create_kb = st.form_submit_button(
                "Create",
                # disabled=not bool(kb_name),
                use_container_width=True,
            )

        if submit_create_kb:
            if not kb_name or not kb_name.strip():
                st.error(f"Knowledge base name cannot be empty!")
            elif kb_name in kb_list:
                st.error(f"{kb_name} Knowledge base already exists!")
            else:
                ret = api.create_knowledge_base(
                    knowledge_base_name=kb_name,
                    embed_model=embed_model,
                )
                st.toast(ret.get("msg", " "))
                st.session_state["selected_kb_name"] = kb_name
                st.session_state["selected_kb_info"] = kb_info
                st.rerun()

    elif selected_kb:
        kb = selected_kb
        st.session_state["selected_kb_info"] = kb_list[kb]['kb_info']
        # 上传文件
        files = st.file_uploader("Upload Knowledge Document：",
                                 [i for ls in LOADER_DICT.values() for i in ls],
                                 accept_multiple_files=True,
                                 )
        kb_info = st.text_area("Please Input Knowledge base Introduction:", value=st.session_state["selected_kb_info"], max_chars=None, key=None,
                               help=None, on_change=None, args=None, kwargs=None)

        if kb_info != st.session_state["selected_kb_info"]:
            st.session_state["selected_kb_info"] = kb_info
            api.update_kb_info(kb, kb_info)

        # with st.sidebar:
        with st.expander(
                "Document processing configuration",
                expanded=True,
        ):
            cols = st.columns(3)
            chunk_size = cols[0].number_input("Maximum length of a single chunk", 1, 1000, CHUNK_SIZE)
            chunk_overlap = cols[1].number_input("Adjacent text overlap length:", 0, chunk_size, OVERLAP_SIZE)
            cols[2].write("")
            cols[2].write("")
            zh_title_enhance = cols[2].checkbox("Enable title enhancement", ZH_TITLE_ENHANCE)

        if st.button(
                "Add files to the knowledge base",
                # use_container_width=True,
                disabled=len(files) == 0,
        ):
            ret = api.upload_kb_docs(files,
                                     knowledge_base_name=kb,
                                     override=True,
                                     chunk_size=chunk_size,
                                     chunk_overlap=chunk_overlap,
                                     zh_title_enhance=zh_title_enhance)
            if msg := check_success_msg(ret):
                st.toast(msg, icon="✔")
            elif msg := check_error_msg(ret):
                st.toast(msg, icon="✖")

        st.divider()

        # 知识库详情
        # st.info("请选择文件，点击按钮进行操作。")
        doc_details = pd.DataFrame(get_kb_file_details(kb))
        if not len(doc_details):
            st.info(f"Knowledge base `{kb}` is empty")
        else:
            st.write(f"Existing documents in Knowledge base `{kb}`:")
            st.info("The knowledge base contains source files and vector libraries. Please select the files from the table below and operate.")
            doc_details.drop(columns=["kb_name"], inplace=True)
            doc_details = doc_details[[
                "No", "file_name", "document_loader", "text_splitter", "docs_count", "in_folder", "in_db",
            ]]
            # doc_details["in_folder"] = doc_details["in_folder"].replace(True, "✓").replace(False, "×")
            # doc_details["in_db"] = doc_details["in_db"].replace(True, "✓").replace(False, "×")
            gb = config_aggrid(
                doc_details,
                {
                    ("No", "No"): {},
                    ("file_name", "file_name"): {},
                    # ("file_ext", "文档类型"): {},
                    # ("file_version", "文档版本"): {},
                    ("document_loader", "document_loader"): {},
                    ("docs_count", "docs_count"): {},
                    ("text_splitter", "text_splitter"): {},
                    # ("create_time", "创建时间"): {},
                    ("in_folder", "in_folder"): {"cellRenderer": cell_renderer},
                    ("in_db", "in_db"): {"cellRenderer": cell_renderer},
                },
                "multiple",
            )

            doc_grid = AgGrid(
                doc_details,
                gb.build(),
                columns_auto_size_mode="FIT_CONTENTS",
                theme="alpine",
                custom_css={
                    "#gridToolBar": {"display": "none"},
                },
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False
            )

            selected_rows = doc_grid.get("selected_rows", [])

            cols = st.columns(5)
            file_name, file_path = file_exists(kb, selected_rows)
            if file_path:
                with open(file_path, "rb") as fp:
                    cols[0].download_button(
                        "Download Selected Document",
                        fp,
                        file_name=file_name,
                        use_container_width=True, )
            else:
                cols[0].download_button(
                    "Download Selected Document",
                    "",
                    disabled=True,
                    use_container_width=True, )

            if cols[1].button(
                    "View the sliced content of the selected document",
                    disabled=not file_path,
                    use_container_width=True,
            ):
                file_names = [row["file_name"] for row in selected_rows]
                resp = api.docs_text_split_content(kb, file_names=file_names)
                st.session_state["selected_splits_info"] = resp

            st.write()
            # 将文件分词并加载到向量库中
            if cols[2].button(
                    "Add back to vector database" if selected_rows and (pd.DataFrame(selected_rows)["in_db"]).any() else "Add to vector database",
                    disabled=not file_exists(kb, selected_rows)[0],
                    use_container_width=True,
            ):
                file_names = [row["file_name"] for row in selected_rows]
                api.update_kb_docs(kb,
                                   file_names=file_names,
                                   chunk_size=chunk_size,
                                   chunk_overlap=chunk_overlap,
                                   zh_title_enhance=zh_title_enhance)
                st.rerun()

            # 将文件从向量库中删除，但不删除文件本身。
            if cols[3].button(
                    "Remove from vector database",
                    disabled=not (selected_rows and selected_rows[0]["in_db"]),
                    use_container_width=True,
            ):
                file_names = [row["file_name"] for row in selected_rows]
                api.delete_kb_docs(kb, file_names=file_names)
                st.rerun()

            if cols[4].button(
                    "Remove from KB",
                    type="primary",
                    use_container_width=True,
            ):
                file_names = [row["file_name"] for row in selected_rows]
                api.delete_kb_docs(kb, file_names=file_names, delete_content=True)
                st.rerun()

        st.divider()

        cols = st.columns(3)

        if cols[0].button(
                "Rebuild vector library based on source files",
                # help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                use_container_width=True,
                type="primary",
        ):
            with st.spinner("The vector library is being reconstructed, please wait patiently and do not refresh or close the page."):
                empty = st.empty()
                empty.progress(0.0, "")
                for d in api.recreate_vector_store(kb,
                                                chunk_size=chunk_size,
                                                chunk_overlap=chunk_overlap,
                                                zh_title_enhance=zh_title_enhance):
                    if msg := check_error_msg(d):
                        st.toast(msg)
                    else:
                        empty.progress(d["finished"] / d["total"], d["msg"])
                st.rerun()

        if cols[2].button(
                "Drop Knowledge base",
                use_container_width=True,
        ):
            ret = api.delete_knowledge_base(kb)
            st.toast(ret.get("msg", " "))
            time.sleep(1)
            st.rerun()

        if st.session_state["selected_splits_info"]:
            response = st.session_state["selected_splits_info"]
            for item in response:
                with st.expander("Vs Type：" + item['vs_type']):
                    contents = item['data']
                    for subItem in contents:
                        for i, content in enumerate(subItem['contents']):
                            st.write(f"The {i + 1}th Chunk：" + f"<div style='color:#666666'>{content}</div>", unsafe_allow_html=True)
