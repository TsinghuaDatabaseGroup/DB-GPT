import time
import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
import matplotlib.pyplot as plt
import os

st.session_state.openai_key = '请填写OpenAI Key'
st.session_state.df = None
st.session_state.prompt_history = []

if st.session_state.df is None:
    uploaded_file = st.file_uploader(
        "选择格式化数据文件",
        type=['csv', 'xlsx'],
    )
    if uploaded_file is not None:
        print(uploaded_file)
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state.df = df

with st.form("Question"):
    question = st.text_input("Question", value="", type="default")
    submitted = st.form_submit_button("Submit")
    if submitted:
        with st.spinner():
            llm = OpenAI(api_token=st.session_state.openai_key)
            file_name = f'{time.time()}.png'
            chart_path = f'./charts/'
            pandas_ai = SmartDataframe(st.session_state.df, config={"llm": llm, "save_charts": True, "save_charts_path": chart_path, "file_name": file_name})
            res = pandas_ai.chat(question)

            if isinstance(res, SmartDataframe) or isinstance(res, pd.DataFrame):
                st.write(res.dataframe.to_html(escape=False, index=False), unsafe_allow_html=True)
            elif res is None:
                if os.path.isfile(chart_path+file_name):
                    im = plt.imread(chart_path+file_name)
                    st.image(im)
                    os.remove(chart_path+file_name)
                else:
                    st.write("No chart generated")
            else:
                st.write(res)

if st.session_state.df is not None:
    st.subheader("Current dataframe:")
    st.write(st.session_state.df)