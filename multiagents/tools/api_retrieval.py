from multiagents.llms.sentence_embedding import sentence_embedding
import numpy as np
import inspect
import random
import sys
import os


class APICaller:

    def __init__(self):
        self.functions = {}
    
    def register_function(self, func_name, params, func, definition):

        query = func_name + " " + " ".join(params)

        embedding_file_name = f"./multiagents/tools/embeddings/local/{func_name}.npy"
        if os.path.exists(embedding_file_name):
            api_embedding = list(np.load(embedding_file_name))
        else:
            api_embedding = sentence_embedding(query)
            np.save(embedding_file_name, api_embedding)

        self.functions[func_name] = {
            "func": func,
            "desc": params,
            "embedding": api_embedding,
            "definition": definition
        }
    
    def call_function(self, func_name, *args, **kwargs):
        if func_name in self.functions:
            func = self.functions[func_name]["func"]
            return func(*args, **kwargs)
        else:
            print(f"Function '{func_name}' not registered.")

            return None

def get_function_parameters(func):
    if sys.version_info >= (3, 10):
        signature = inspect.signature(func)
        return list(signature.parameters.keys())
    else:
        signature = inspect.signature(func)
        parameters = signature.parameters.values()
        return [param.name for param in parameters]

def register_functions_from_module(module, caller, agent_name):
    members = inspect.getmembers(module, inspect.isfunction)

    api_cnt = 0
    agent_name = agent_name.lower()

    for member in members:
        if len(member) == 2:
            name, func = member
        else:
            name, _, func = member

        if func.__module__ == module.__name__:
            functions = getattr(module, "FUNCTION_DEFINITION", {})
            func_definition = functions.get(name, None)

            params = get_function_parameters(func)
            caller.register_function(name, params, func, func_definition)


# def register_functions_from_module(module, caller, max_api_num, agent_name):
#     members = inspect.getmembers(module, inspect.isfunction)

#     # 从members中随机选择前max_api_num个函数（如果数量不足则选择全部）
#     # if len(members) > max_api_num:
#     #     members = random.sample(members, max_api_num)

#     api_cnt = 0
#     necessary_names = ["match_diagnose_knowledge", "whether_is_abnormal_metric"]
#     agent_name = agent_name.lower()
#     # if "expert" in agent_name:
#     #     necessary_names[0] = agent_name.split('expert')[0] + '_' + necessary_names[0]

#     for member in members:
#         if len(member) == 2:
#             name, func = member
#         else:
#             name, _, func = member

#         if func.__module__ == module.__name__:
#             functions = getattr(module, "FUNCTION_DEFINITION", {})
#             func_definition = functions.get(name, None)

#             if name in necessary_names:
#                 params = get_function_parameters(func)
#                 caller.register_function(name, params, func, func_definition)
#             elif name not in necessary_names and api_cnt < max_api_num:
                
#                 api_cnt = api_cnt + 1
                        
#                 params = get_function_parameters(func)
#                 caller.register_function(name, params, func, func_definition)