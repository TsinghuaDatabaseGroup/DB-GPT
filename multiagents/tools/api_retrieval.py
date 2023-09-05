import inspect
import pdb

class APICaller:

    def __init__(self):
        self.functions = {}
    
    def register_function(self, func_name, func):
        self.functions[func_name] = {"func": func, "desc": ""}
    
    def call_function(self, func_name, *args, **kwargs):
        if func_name in self.functions:
            func = self.functions[func_name]["func"]
            return func(*args, **kwargs)
        else:
            raise ValueError(f"Function '{func_name}' not registered.")

def register_functions_from_module(module, caller):
    members = inspect.getmembers(module, inspect.isfunction)

    for name, func in members:
        if func.__module__ == module.__name__:
            caller.register_function(name, func)
