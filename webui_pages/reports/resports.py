import streamlit as st

from server.utils import reports_webui_address
from webui_pages.utils import *


def reports_page(api: ApiRequest, is_lite: bool = False):

    css = """
    <style>
        .st-emotion-cache-z5fcl4 {
            padding: 40px 0 0 0;
            overflow: hidden;
        }
    </style>
    """
    st.write(css, unsafe_allow_html=True)

    with st.spinner('Loading...'):
        st.markdown(f"""<div style="width: 100%; height: calc(100vh - 50px);">
            <iframe src="{reports_webui_address()}" width="100%" height="100%" frameborder="0">
                Your browser does not support iframe.
            </iframe>
        </div>""", unsafe_allow_html=True)
    st.spinner()



