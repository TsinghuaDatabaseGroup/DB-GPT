import time

import streamlit as st
from webui_pages.utils import *
from server.knowledge_base.utils import KNOWLEDGE_EXTRACTION_FILE_DICT


def knowledge_extraction_page(api: ApiRequest, is_lite: bool = None):
    if "knowledge_extractioning" not in st.session_state:
        st.session_state["knowledge_extractioning"] = False

    if "knowledge_extraction_api" not in st.session_state:
        st.session_state["knowledge_extraction_api"] = None

    if "task_output" not in st.session_state:
        st.session_state["task_output"] = ""

    if "upload_and_knowledge_extraction_clicked" not in st.session_state:
        st.session_state["upload_and_knowledge_extraction_clicked"] = False

    if st.session_state["knowledge_extractioning"]:
        knowledge_extraction_process(api)

    file = st.file_uploader("上传原始知识文件：", [i for ls in KNOWLEDGE_EXTRACTION_FILE_DICT.values() for i in ls],
                            accept_multiple_files=False)
    if st.button("上传并提取"):
        st.session_state["upload_and_knowledge_extraction_clicked"] = True

    if st.session_state["upload_and_knowledge_extraction_clicked"]:
        st.write("上传文件中...")
        filename = file.name
        file_content = file.read()
        resp = api.run_knowledge_extraction(filename, file_content)
        if msg := check_error_msg(resp):
            st.error(msg)
            reset_session_state()
            return
        st.write("上传成功, 开始提取知识...")
        st.session_state["knowledge_extractioning"] = True
        knowledge_extraction_process(api)


def knowledge_extraction_process(api):
    with (st.status(label="任务执行中...", expanded=True) as status):
        code_placeholder = st.empty()
        while True:
            response = api.knowledge_extraction_output()
            if msg := check_error_msg(response):
                st.error(msg)
                reset_session_state()
                return
            if not response["is_alive"]:
                status.update(label="没有提取任务在运行", expanded=True, state="complete")
                break
            st.session_state["task_output"] = str(response["output"])
            code_placeholder.code(st.session_state["task_output"], language='powershell')
            time.sleep(2)  # wait for 2 seconds before polling again
        reset_session_state()


def reset_session_state():
    st.session_state["knowledge_extractioning"] = False
    st.session_state["upload_and_knowledge_extraction_clicked"] = False
