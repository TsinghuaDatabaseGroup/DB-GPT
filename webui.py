import streamlit as st

from webui_pages.diagnose import diagnose_page
from webui_pages.reports.resports import reports_page
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages.dialogue.dialogue import dialogue_page
from webui_pages.knowledge_base import knowledge_base_page

import os
import sys
from configs import VERSION
from server.utils import api_address


api = ApiRequest(base_url=api_address())

if __name__ == "__main__":
    is_lite = "lite" in sys.argv

    st.set_page_config(
        "DB-GPT",
        os.path.join("img", "chat_icon_blue_square_v2.png"),
        layout="wide",
        initial_sidebar_state="expanded"
    )

    css = """
    <style>
        .block-container {
            padding-left: 20px !important;
            padding-right: 20px !important;
            padding-top: 40px !important;
            padding-bottom: 40px !important;
        }
    </style>
    """
    st.write(css, unsafe_allow_html=True)

    pages = {
        "Knowledge Base": {
            "icon": "hdd-stack",
            "func": knowledge_base_page,
        },
        "Chat": {
            "icon": "chat",
            "func": dialogue_page,
        },
        "Diagnosis": {
            "icon": "heart-pulse",
            "func": diagnose_page,
        },
        "History": {
            "icon": "file-earmark-text",
            "func": reports_page,
        }
    }

    with st.sidebar:
        st.caption(
            f"""<p align="right">D-Bot Version：{VERSION}</p>""",
            unsafe_allow_html=True,
        )
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            "",
            options=options,
            icons=icons,
            default_index=default_index,
        )

    if selected_page in pages:
        pages[selected_page]["func"](api=api, is_lite=is_lite)
