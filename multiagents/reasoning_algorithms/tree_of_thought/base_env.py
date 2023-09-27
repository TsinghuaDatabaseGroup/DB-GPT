

class base_env:


    def __init__(self):
        self.task_description = ""
        self.input_description = ""
        self.tool_names = []
        self.functions = []

    def restart(self):
        '''
        重启环境
        '''
        raise NotImplementedError
    
    def get_score(self):
        '''
        获取当前状态的价值
        伪造的函数，用来在oracle模式进行搜索，实际上用不到(也不可能获取到)
        '''
        raise NotImplementedError

    def step(self,action,input_str):
        '''
        在自然语言模态进行一次交互
        返回值 (输出str, 状态码)
        '''
        raise NotImplementedError
    
    def check_success(self):
        '''
        如果已经成功，返回1，否则返回0
        '''
        raise NotImplementedError
    
    def to_json(self):
        '''
        重启环境
        '''
        raise NotImplementedError