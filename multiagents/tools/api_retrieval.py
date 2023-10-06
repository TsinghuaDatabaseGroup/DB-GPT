import inspect
import pdb
import random

class APICaller:

    def __init__(self):
        self.functions = {}
    
    def register_function(self, func_name, params, func):
        self.functions[func_name] = {"func": func, "desc": params}
    
    def call_function(self, func_name, *args, **kwargs):
        if func_name in self.functions:
            func = self.functions[func_name]["func"]
            return func(*args, **kwargs)
        else:
            print(f"Function '{func_name}' not registered.")

            return None

def register_functions_from_module(module, caller):
    members = inspect.getmembers(module, inspect.isfunction)

    max_api_num = 20
    # randomly select top max_api_num (can be fewer) from members
    if len(members) > max_api_num:
        members = random.sample(members, max_api_num)

    for name, params, func in members:
        if func.__module__ == module.__name__:
            caller.register_function(name, params, func)