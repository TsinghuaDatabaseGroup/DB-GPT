"""Interface for tools."""

class RequestAPI:
    def __init__(self):
        self.functions = {}
    
    def register_api(self, func_name, func):
        self.functions[func_name] = func
    
    def call_api(self, func_name, *args, **kwargs):
        if func_name in self.functions:
            func = self.functions[func_name]
            return func(*args, **kwargs)
        else:
            raise ValueError(f"Function '{func_name}' not registered.")
