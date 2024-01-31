import streamlit as st
from streamlit.components.v1 import declare_component
from webui_pages.utils import *
import os

def reports_page(api: ApiRequest, is_lite: bool = False):
    if "model_list" not in st.session_state:
        st.session_state["model_list"] = api.diagnose_diagnose_llm_model_list()

    if "current_model" not in st.session_state:
        st.session_state["current_model"] = st.session_state["model_list"][0]

    st.session_state["diagnose_histories"] = api.diagnose_histories(model=st.session_state["current_model"])

    my_component = declare_component("my_component", path=os.path.join(os.path.dirname(__file__), 'reports_ui/build_dist'))
    # my_component = declare_component("my_component", url='http://localhost:3001')
    response = my_component(args={
        "modelList": st.session_state["model_list"],
        "currentModel": st.session_state["current_model"],
        "diagnoseHistories": st.session_state["diagnose_histories"]
    }, key="my_component")
    try:
        if response["model"] and response["model"] != st.session_state["current_model"]:
            st.session_state["current_model"] = response["model"]
            st.session_state["diagnose_histories"] = api.diagnose_histories(model=st.session_state["current_model"])
            st.rerun()
    except Exception as e:
        print(e)




