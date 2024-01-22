import time

import streamlit as st
from webui_pages.utils import *
from server.knowledge_base.utils import DIAGNOSE_FILE_DICT
from server.knowledge_base.kb_service.base import get_kb_details


def diagnose_page(api: ApiRequest, is_lite: bool = None):
    try:
        kb_list = {x["kb_name"]: x for x in get_kb_details()}
    except Exception as e:
        st.error("There is an error in obtaining knowledge base information. Please check whether the initialization or migration has been completed according to the steps of `4 Knowledge Base Initialization and Migration` in `README.md`, or whether there is a database connection error.")
        # st.error("获取知识库信息错误，请检查是否已按照 `README.md` 中 `4 知识库初始化与迁移` 步骤完成初始化或迁移，或是否为数据库连接错误。")
        st.stop()
    kb_names = list(kb_list.keys())

    if "selected_kb_name" in st.session_state and st.session_state["selected_kb_name"] in kb_names:
        selected_kb_index = kb_names.index(st.session_state["selected_kb_name"])
    else:
        selected_kb_index = 0

    if "selected_kb_info" not in st.session_state:
        st.session_state["selected_kb_info"] = ""

    if "diagnosing" not in st.session_state:
        st.session_state["diagnosing"] = False
    
    if "diagnose_api" not in st.session_state:
        st.session_state["diagnose_api"] = None

    if "task_output" not in st.session_state:
        st.session_state["task_output"] = ""

    if "upload_and_diagnose_clicked" not in st.session_state:
        st.session_state["upload_and_diagnose_clicked"] = False

    def format_selected_kb(kb_name: str) -> str:
        if kb := kb_list.get(kb_name):
            return f"{kb_name} ({kb['vs_type']} @ {kb['embed_model']})"
        else:
            return kb_name
    
    selected_kb = st.selectbox(
        "Available knowledge base",
        kb_names,
        format_func=format_selected_kb,
        index=selected_kb_index
    )

    if st.session_state["diagnosing"]:
        diagnose_process(api)

    file = st.file_uploader("Upload Anomaly File：", [i for ls in DIAGNOSE_FILE_DICT.values() for i in ls], accept_multiple_files=False)
    if st.button("Upload and Diagnosis"):
        st.session_state["upload_and_diagnose_clicked"] = True

    if st.session_state["upload_and_diagnose_clicked"]:
        st.write("Uploading...")
        filename = file.name
        file_content = file.read()
        resp = api.diagnose_file(filename, file_content)
        if msg := check_error_msg(resp):
            st.error(msg)
            reset_session_state()
            return
        st.write("Upload Success, Start Diagnosis!")
        st.session_state["diagnosing"] = True
        diagnose_process(api)


def diagnose_process(api):
    with (st.status(label="Diagnosing...", expanded=True) as status):
        code_placeholder = st.empty()
        while True:
            response = api.diagnose_output()
            if msg := check_error_msg(response):
                st.error(msg)
                reset_session_state()
                return
            if not response["is_alive"]:
                status.update(label="No diagnosis task is being executed...", expanded=True, state="complete")
                break
            st.session_state["task_output"] = str(response["output"])
            code_placeholder.code(st.session_state["task_output"], language='powershell')
            time.sleep(2)  # wait for 2 seconds before polling again
        reset_session_state()

def reset_session_state():
    st.session_state["diagnosing"] = False
    st.session_state["upload_and_diagnose_clicked"] = False
