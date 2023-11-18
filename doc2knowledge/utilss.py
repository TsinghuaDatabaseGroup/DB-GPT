from pyheaven import *
from prompts import *

import time
from openai import OpenAI
import itertools

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
            self.config = get_config('openai-api')
            self.client = OpenAI(
                api_key=self.config['api_key'],
                organization = self.config['organization']
            )

            self.model = backend.split('_')[-1]
        else:
            pass
        
    def Query(self, messages, temperature=0, functions=list(), retry_gap=0.1, timeout=3):
        
        
        identifier = "|".join([self.backend, str(messages)] + ([str(functions)] if functions else []))
        
        #response = get_cache(identifier)
        response = None
        if response is not None:
            return response
        while timeout>0:
            try:
                if functions:
                    assert (self.model=='gpt-4'), f"Functions are only supported in 'gpt-4'!"
                    response = self.client.chat.completions.create(
                        model = self.model,
                        messages = messages,
                        functions = functions,
                        temperature = temperature,
                    )
                else:
                    response = self.client.chat.completions.create(
                        model = self.model,
                        messages = messages,
                        temperature = temperature,
                    )
                response = response.choices[0].message

                # update_cache(identifier, response)
                return response
            except KeyboardInterrupt as e:
                exit(0)
            except NotImplementedError as e:
                exit(0)
            except Exception as e:
                print(ERROR(e))
                time.sleep(retry_gap)
                print(ERROR(f"Retrying..."))
                timeout -= 1
        return None