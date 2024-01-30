import time
import re
import streamlit as st
from streamlit.components.v1 import declare_component
import os
from webui_pages.utils import *
from server.knowledge_base.utils import DIAGNOSE_FILE_DICT

def diagnose_page(api: ApiRequest, is_lite: bool = None):
    if 'diagnosing' not in st.session_state:
        st.session_state['diagnosing'] = False

    if 'diagnose_api' not in st.session_state:
        st.session_state['diagnose_api'] = None

    if 'diagnose_file' not in st.session_state:
        st.session_state['diagnose_file'] = None

    if 'task_output' not in st.session_state:
        st.session_state['task_output'] = ''

    if 'upload_and_diagnose_clicked' not in st.session_state:
        st.session_state['upload_and_diagnose_clicked'] = False

    if 'upload_and_diagnose_clicked' not in st.session_state:
        st.session_state['upload_and_diagnose_clicked'] = False

    if 'diagnose_component' not in st.session_state:
        st.session_state['diagnose_component'] = False

    if 'node_data' not in st.session_state:
        st.session_state['node_data'] = {
            'nodes': [
                {
                    'id': 'A',
                    'userData': {
                        'title': '初始化专家角色',
                        'content': '',
                        'isCompleted': False,
                        'isRuning': False
                    },
                    'render': 'titleContentNode',
                    'top': 20,
                    'left': 120,
                    'endpoints': [
                        {
                            'id': 'bottom',
                            'orientation': [0, 1]
                        }
                    ]
                },
                {
                    'id': 'B',
                    'userData': {
                        'title': '初始化诊断报告',
                        'content': '',
                        'isCompleted': False,
                        'isRuning': False
                    },
                    'render': 'titleContentNode',
                    'top': 150,
                    'left': 120,
                    'endpoints': [
                        {
                            'id': 'top',
                            'orientation': [0, -1]
                        },
                        {
                            'id': 'bottom',
                            'orientation': [0, 1]
                        }
                    ]
                },
                {
                    'id': 'C',
                    'userData': {
                        'title': '根据异常分配诊断专家',
                        'content': '',
                        'isCompleted': False,
                        'isRuning': False
                    },
                    'render': 'titleContentNode',
                    'top': 280,
                    'left': 120,
                    'endpoints': [
                        {
                            'id': 'top',
                            'orientation': [0, -1]
                        },
                        {
                            'id': 'bottom',
                            'orientation': [0, 1]
                        }
                    ]
                },
                {
                    'id': 'D',
                    'userData': {
                        'title': '专家诊断',
                        'content': '',
                        'isCompleted': False,
                        'isRuning': False,
                        'expertData': []
                    },
                    'render': 'agentGroupNode',
                    'top': 410,
                    'left': 40,
                    'endpoints': [
                        {
                            'id': 'top',
                            'orientation': [0, -1]
                        },
                        {
                            'id': 'bottom',
                            'orientation': [0, 1]
                        }
                    ]
                },
                {
                    'id': 'E',
                    'userData': {
                        'title': '圆桌讨论',
                        'content': '',
                        'isCompleted': False,
                        'isRuning': False,
                        'expertData': []
                    },
                    'render': 'titleContentNode',
                    'top': 610,
                    'left': 120,
                    'endpoints': [
                        {
                            'id': 'top',
                            'orientation': [0, -1]
                        },
                        {
                            'id': 'bottom',
                            'orientation': [0, 1]
                        }
                    ]
                },
                {
                    'id': 'F',
                    'userData': {
                        'title': '报告生成',
                        'content': '',
                        'isCompleted': False,
                        'isRuning': False
                    },
                    'render': 'titleContentNode',
                    'top': 740,
                    'left': 120,
                    'endpoints': [
                        {
                            'id': 'top',
                            'orientation': [0, -1]
                        }
                    ]
                }
            ],
            'edges': [
                {
                    'id': '1',
                    'source': 'bottom',
                    'target': 'top',
                    'sourceNode': 'A',
                    'targetNode': 'B',
                    'type': 'endpoint'
                },
                {
                    'id': '2',
                    'source': 'bottom',
                    'target': 'top',
                    'sourceNode': 'B',
                    'targetNode': 'C',
                    'type': 'endpoint'
                },
                {
                    'id': '3',
                    'source': 'bottom',
                    'target': 'top',
                    'sourceNode': 'C',
                    'targetNode': 'D',
                    'type': 'endpoint'
                },
                {
                    'id': '4',
                    'source': 'bottom',
                    'target': 'top',
                    'sourceNode': 'D',
                    'targetNode': 'E',
                    'type': 'endpoint'
                },
                {
                    'id': '5',
                    'source': 'bottom',
                    'target': 'top',
                    'sourceNode': 'E',
                    'targetNode': 'F',
                    'type': 'endpoint'
                }
            ]
        }

    deal_node_data()

    col1, col2 = st.columns([2, 3])

    with col1:
        st.session_state['diagnose_component'] = declare_component('my_component', path=os.path.join(os.path.dirname(__file__), 'build_dist'))
        args = {'width': '40%', 'height': '860px', 'nodeData': st.session_state['node_data']}
        st.session_state['diagnose_component'](args=args)

    with col2:

        st.session_state['diagnose_file'] = st.file_uploader('Upload Anomaly File：', [i for ls in DIAGNOSE_FILE_DICT.values() for i in ls], accept_multiple_files=False, disabled=st.session_state['diagnosing'])
        if st.button('Upload and Diagnosis'):
            st.session_state['upload_and_diagnose_clicked'] = True

        if st.session_state['upload_and_diagnose_clicked']:
            if st.session_state['diagnose_file']:
                filename = st.session_state['diagnose_file'].name
                file_content = st.session_state['diagnose_file'].read()
                resp = api.diagnose_file(filename, file_content)
                if msg := check_error_msg(resp):
                    st.error(msg)
                    reset_session_state()
                    return
            st.write('Upload Success, Start Diagnosis!')
            st.session_state['diagnosing'] = True
            diagnose_process(api)

        if st.session_state['diagnosing']:
            diagnose_process(api)


def extract_flows(log_text):
    pattern = r'<flow>(.*?)</flow>'
    matches = re.findall(pattern, log_text)

    flow_jsons = []
    for match in matches:
        match = match.replace("'", '"')
        print('****match:', match)
        try:
            flow_json = json.loads(match)
            flow_jsons.append(flow_json)
            print('****flow_json:', flow_json)
        except json.JSONDecodeError:
            print("Could not decode string to json: {match}")

    return flow_jsons


def remove_duplicates(flows):
    """
    过滤数组，如果对象的title一样，则只保留后面那个。
    """
    temp_dict = {}
    for flow in flows:
        title = flow['title']
        temp_dict[title] = flow
    unique_flows = list(temp_dict.values())
    return unique_flows

def deal_node_data():
    text = st.session_state['task_output']
    flows = extract_flows(text)
    flows = remove_duplicates(flows)

    for (index, node) in enumerate(st.session_state['node_data']['nodes']):
        user_data = node['userData']
        for flow in flows:
            if user_data.get('title') == flow.get("title"):
                node['userData'] = flow
                st.session_state['node_data']['nodes'][index] = node
                continue


def diagnose_process(r_api):
    with st.container(height=500):
        with (st.status(label='Diagnosing...', expanded=True) as status):
            code_placeholder = st.empty()
            while True:
                response = r_api.diagnose_output()
                if msg := check_error_msg(response):
                    st.error(msg)
                    reset_session_state()
                    return
                if not response['is_alive']:
                    status.update(label='No diagnosis task is being executed...', expanded=True, state='complete')
                    break
                st.session_state['task_output'] = str(response['output'])
                code_placeholder.code(st.session_state['task_output'], language='powershell')
                time.sleep(2)
                deal_node_data()
                print("=============st.rerun()==============")
                st.rerun()
                # wait for 2 seconds before polling again
            reset_session_state()

def reset_session_state():
    st.session_state['diagnosing'] = False
    st.session_state['upload_and_diagnose_clicked'] = False
    st.session_state['diagnose_file'] = None
