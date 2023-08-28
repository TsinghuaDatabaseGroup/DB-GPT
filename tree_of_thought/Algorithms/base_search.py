

class base_search_method:


    def __init__(self):
        pass


    def to_json(self):
        '''
        可以写回生成的搜索结果，保证含有
        "answer_generation": {
            "valid_data": bool,
            "final_answer": string,
            "chain": [
                {
                    "thought":string,
                    "action_name":string,
                    "action_input":string,
                    "observation": string,
                }
            ],
        }
        作为answer生成的数据
        '''
        raise NotImplementedError


    def start(self):
        raise NotImplementedError


