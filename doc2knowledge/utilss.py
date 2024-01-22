from pyheaven import *
from prompts import *

import time
from openai import OpenAI
import itertools
import requests
from termcolor import colored

# config utils
def get_config(key):
    return LoadJson("config.json")[key]

def get_cache(key):
    key = key.lower().strip()

    if not ExistFile("cache.json"):
        SaveJson(dict(), "cache.json")
    
    cache = LoadJson("cache.json")
    if key in cache:
        return cache[key]
        # crea
    return None

# cache utils
def update_cache(key, value, update=False):
    key = key.lower().strip()
    cache = LoadJson("cache.json")
    if update or (key not in cache):
        cache[key] = value
    SaveJson(cache, "cache.json")

def clear_cache():
    SaveJson(dict(), "cache.json")

# file utils
def str2id(id_str):
    return tuple(int(j) for j in id_str.split('.'))

def parse_id(file_name):
    return str2id(file_name.split(' ')[0])

def parse_depth(file_name):
    return len(parse_id(file_name))

def is_father(file_name1, file_name2):

    id1 = parse_id(file_name1)
    id2 = parse_id(file_name2)
    if id1 == id2[:-1]:
        return True
    elif id1 == (0,) and len(id2) == 1 and id2[0] > 0:
        return True

    return False

    return parse_id(file_name1) == parse_id(file_name2)[:-1]

def id_sort(nodes, reverse=False):
    return sorted(nodes, key=lambda x: x['id'], reverse=reverse)

def topo_sort(nodes):
    nodes = id_sort(nodes)
    for i, node in enumerate(nodes):
        nodes[i]['book'] = len(node['children'])
    nodes = {node['id_str']: node for node in nodes}
    sorted_nodes = [nodes[key] for key in nodes if nodes[key]['book']==0]; head = 0
    while head < len(sorted_nodes):
        v = sorted_nodes[head]; head += 1
        if v['father']:
            nodes[v['father']]['book'] -= 1
            if not nodes[v['father']]['book']:
                sorted_nodes.append(nodes[v['father']])
    return [{k:v for k,v in node.items() if k!='book'} for node in sorted_nodes]

def read_txt(file_path):
    assert ExistFile(file_path), f"File not found: {file_path}"
    with open(file_path, "r") as f:
        return f.read().strip()

# openai utils
class LLMCore(object):
    def __init__(self, backend="openai_gpt-3.5-turbo"):
        self.backend = backend
        if self.backend.startswith("openai_"):

            # self.config = get_config('openai-api')
            # self.client = OpenAI(
            #     api_key=self.config['api_key'],
            #     organization = self.config['organization']
            # )
            
            self.model = backend.split('_')[-1]
            
        else:
            pass
        
    def Query(self, messages, temperature=0, functions=list(), retry_gap=0.1, timeout=10):
        
        
        identifier = "|".join([self.backend, str(messages)] + ([str(functions)] if functions else []))
        
        #response = get_cache(identifier)
        # if response is not None:
        #     return response

        api_key = os.environ.get("OPENAI_API_KEY")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        }
        url = "https://api.aiaiapi.com/v1/chat/completions"

        cur_timeout = timeout
        while cur_timeout>0:
            try:
                if functions:
                    # assert (self.model=='gpt-4'), f"Functions are only supported in 'gpt-4'!"
                    
                    payload = {
                        "model": "gpt-4-1106-preview", # "gpt-4-1106-preview", # "gpt-3.5-turbo-16k",#"gpt-4-32k-0613",
                        "messages": messages,
                        "functions": functions,
                        "temperature": temperature,
                    }

                    response = requests.post(url, json=payload, headers=headers)


                    # response = self.client.chat.completions.create(
                    #     model = self.model,
                    #     messages = messages,
                    #     functions = functions,
                    #     temperature = temperature,
                    # )
                else:

                    payload = {
                        "model": "gpt-4-1106-preview", # "gpt-4-1106-preview", # "gpt-3.5-turbo-16k",#"gpt-4-32k-0613",
                        "messages": messages,
                        "temperature": temperature,
                    }

                    response = requests.post(url, json=payload, headers=headers)

                    # response = self.client.chat.completions.create(
                    #     model = self.model,
                    #     messages = messages,
                    #     temperature = temperature,
                    # )
                
                output = json.loads(response.text)
                
                if "choices" in output:
                    output = output["choices"][0]["message"]
                    return output
                else:
                    if cur_timeout % timeout == 0:
                        print(colored("Fail to prase the response: " + str(response.text), "red"))

                # response = response.choices[0].message

                # update_cache(identifier, response)

            except Exception as e:
                # print(ERROR(e))
                time.sleep(retry_gap)
            
            cur_timeout -= 1
        
        return None