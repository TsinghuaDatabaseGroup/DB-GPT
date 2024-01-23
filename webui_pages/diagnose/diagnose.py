import time

import streamlit as st
from webui_pages.utils import *
from server.knowledge_base.utils import DIAGNOSE_FILE_DICT

def diagnose_page(api: ApiRequest, is_lite: bool = None):

    if "diagnosing" not in st.session_state:
        st.session_state["diagnosing"] = False
    
    if "diagnose_api" not in st.session_state:
        st.session_state["diagnose_api"] = None

    if "task_output" not in st.session_state:
        st.session_state["task_output"] = ""

    if "upload_and_diagnose_clicked" not in st.session_state:
        st.session_state["upload_and_diagnose_clicked"] = False

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
