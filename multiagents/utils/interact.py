import time
from configs import DIAGNOSE_USER_FEEDBACK_PATH, DIAGNOSE_RUN_DATA_PATH, DIAGNOSE_RUN_DATA_COPY_PATH, IS_FEEDBACK_BY_UI
import shutil
import json


def user_input(placeholder):
    if IS_FEEDBACK_BY_UI:
        while True:
            try:
                with open(DIAGNOSE_USER_FEEDBACK_PATH, 'r+') as f:
                    content = f.read().strip()
                    if len(content) > 0:
                        input_content = content
                        # 清空文件内容
                        f.seek(0)
                        f.truncate()
                        break
                    else:
                        time.sleep(0.1)
            except Exception as err:
                print('Error: ', err, flush=True)
                time.sleep(0.1)
    else:
        input_content = input(placeholder)
    return input_content

def init_messages():
    shutil.copy(DIAGNOSE_RUN_DATA_COPY_PATH, DIAGNOSE_RUN_DATA_PATH)

def set_cur_task(cur_task):
    assert cur_task in ['roleAssignment', 'expertDiagnosis', 'groupDiscussion', 'reportGeneration', 'reportDemonstration']
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        state['currentTask'] = cur_task
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))

def _add_message(state, cur_task, role, message, flag=True):
    message['sender'] = role if flag else 'D-Bot'
    if cur_task == 'expertDiagnosis':
        for expert in state[cur_task]['experts']:
            if expert['name'] == role:
                expert['messages'].append(message)
                break
    else:
        state[cur_task]['messages'].append(message)

def add_display_message(cur_task, role, message, time, flag=True):
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        _add_message(state, cur_task, role, {"data": message, "time": time}, flag)
        state['needInput'] = False
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))

def add_feedback_message(cur_task, role, placeholder, message, time):
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        _add_message(state, cur_task, role, {"data": message, "time": time})
        state['needInput'] = True
        state['placeholder'] = placeholder
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))


def finish_feedback_message():
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        state['needInput'] = False
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))


def finish_select_edit_message(cur_task, role):
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        if cur_task == 'expertDiagnosis':
            for expert in state[cur_task]['experts']:
                if expert['name'] == role:
                    expert['messages'][-1]['edit'] = False
                    break
        else:
            state[cur_task]['messages'][-1]['edit'] = False
        state['needInput'] = False
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))

def add_select_message(cur_task, role, message, time, select_list):
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        _add_message(state, cur_task, role, {"data": message, "time": time, "edit": True, "type": "select", "selectList": select_list})
        state['needInput'] = False
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))

def add_edit_message(cur_task, role, placeholder, message, time):
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        _add_message(state, cur_task, role, {"data": message, "time": time, "edit": True})
        state['needInput'] = False
        state['placeholder'] = placeholder
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))

def add_experts(selected_experts):
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        state['expertDiagnosis']['experts'] = [{'name': e, 'messages': [], "complete": False} for e in selected_experts]
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))

def add_report(report):
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        state['reportDemonstration'] = report
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))

def finish_expert_diagnosis(role):
    with open(DIAGNOSE_RUN_DATA_PATH, 'r+') as f:
        state = json.loads(f.read())
        for expert in state['expertDiagnosis']['experts']:
            if expert['name'] == role:
                expert['complete'] = True
                break
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))
