import datetime
import decimal
import os
import uuid
import json
import openai
import yaml
from flask.json import JSONEncoder as BaseJSONEncoder

CHAT_HISTORY_FILE = "chat_history.json"

def read_yaml(config_name, config_path):
    """
    config_name:需要读取的配置内容
    config_path:配置文件路径
    """
    print(config_name)
    if config_name and config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f.read())
        if config_name in conf.keys():
            return conf[config_name]
        else:
            raise KeyError('未找到对应的配置信息')
    else:
        raise ValueError('请输入正确的配置名称或配置文件路径')


# 使用openai
def openai_completion_create(messages):
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_key = openai_api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response


# 将聊天记录保存到chat_history文件中
def save_chat_history(chat_data, analyse_at):
    if not os.path.exists(CHAT_HISTORY_FILE):
        json_data = {}
    else:
        try:
            with open(CHAT_HISTORY_FILE, 'r') as file:
                json_data = json.load(file)
        except Exception as e:
            print(e)
            json_data = {}
    chat_list = json_data.get(analyse_at, [])
    chat_list.append(chat_data)
    json_data[analyse_at] = chat_list
    with open(CHAT_HISTORY_FILE, 'w') as file:
        json.dump(json_data, file, indent=2)


# 获取聊天记录
def get_chat_history():
    if not os.path.exists(CHAT_HISTORY_FILE):
        json_data = {}
    else:
        with open(CHAT_HISTORY_FILE, 'r') as file:
            json_data = json.load(file)
    return json_data