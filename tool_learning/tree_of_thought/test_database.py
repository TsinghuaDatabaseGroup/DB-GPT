import sys
sys.path.append('..')

from LLM.openai_0613 import chatgpt_0613
from termcolor import colored
from Algorithms.UCT_vote_function import UCT_vote_function
from Downstream_tasks.base_env import base_env
import re
import os
import json
from typing import overload
from Downstream_tasks.tool_nolc import load_single_tools,import_all_apis
import pdb

class wrap_diag(base_env):
    def __init__(self,input_description):
        super(wrap_diag, self).__init__()

        self.input_description = input_description

        tool_name, tool_url = 'database',  "http://127.0.0.1:8079/tools/database/"
        tool_name, tool_config = load_single_tools(tool_name, tool_url)

        self.tool, _ = import_all_apis(tool_config)
        self.name_to_tool_map = {tool.name: tool for tool in self.tool}

        self.tool_names = [tool.name for tool in self.tool]

        self.task_description = "The followings is the description of the valid actions:\n"

        for tool in self.tool:
            self.task_description += tool.name + tool.description + "\n"


        pattern_1 = re.compile(r"Your input should be a json \(args json schema\): {(.*)} The Action")
        pattern_2 = re.compile(r"{\"(.*)\" : (.*), }")
        for api in self.tool:
            func_name = api.name
            func_description = api.description

            function = {
                "name": func_name,
                "description": func_description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            }

            param_string = pattern_1.findall(func_description)

            for i in param_string:
                result = pattern_2.findall(i)[0]
                param_name, param_type = result[0], result[1]

                param = {
                    param_name: {
                        "type": param_type,
                        "description": "", # TODO
                    }
                }

                function["parameters"]["properties"].update(param)

            self.functions.append(function)

        self.finish_func = {
            "name": "Finish",
            "description": "If you think you get the result which can answer the input description, call this function to give the final answer",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The final answer you want to give the user"
                    },
                },
                "required": ["answer"]
            }
        }
        self.functions.append(self.finish_func)
        self.tool_names.append(self.finish_func["name"])

        self.restart()

    def check_success(self):
        return self.status

    def to_json(self):
        return {}

    def restart(self):
        self.status = 0

    def get_score(self):
        return 0.0

    def step(self, action_name="",action_input=""):
        # print(action_input)

        if action_name == "Final Answer":
            self.status = 1
            return

        if self.name_to_tool_map.get(action_name):
            observation = self.name_to_tool_map[action_name].run(
                action_input
            )
            # print(observation)
            return observation, 0
        else:
            output = f"no such action : {action_name}"
            # print(output)
            return output, 0

def node_to_chain(node):
    chain = {
        "prompt": "",
        "query": "",
        "chains": [],
        "answer": "",
    }

    step = {}
    for i, message in enumerate(node.messages):
        if message["role"] == "system":
            chain["prompt"] = message["content"]
        elif message["role"] == "user":
            chain["query"] += message["content"]
        elif message["role"] == "assistant":
            if "function_call" in message:
                function_call = message["function_call"]
                if function_call["name"] == "Finish":
                    chain["answer"] = function_call["arguments"]
                else:
                    step["action"] = function_call["name"]
                    step["action_input"] = function_call["arguments"]
            else:
                step["thought"] = message["content"]
        elif message["role"] == "function":
            step["observation"] = message["content"]
            chain["chains"].append(step)
            step = {}

    return chain


def test_single(input_description):
    print(colored(f"now playing {input_description}", "green"))
    env = wrap_diag(input_description)

    pdb.set_trace()        
    llm_forward = chatgpt_0613()
    chain = UCT_vote_function(llm=llm_forward,io_func=env)
    result = chain.start(simulation_count=3,epsilon_new_node=0.3,choice_count=3,vote_candidates=2,vote_count=1,single_chain_max_step=40)
    chain = node_to_chain(result)
    pdb.set_trace()

    return env, chain


if __name__ == "__main__":

    slow_query = "SELECT s_comment FROM part As p,partsupp As ps,supplier As s WHERE p.p_partkey = ps.ps_partkey AND s.s_suppkey = ps.ps_suppkey AND ps.ps_availqty = 6331 AND p.p_type > 'LARGE POLISHED NICKEL' AND p.p_retailprice < 1758.76 ORDER BY s_comment DESC;"

    task = """ Given a SQL query:
    \"{}\"
    
    First, obtain the execution plan for the given SQL query.
    
    Next, assess the query plan's efficacy. If the existing plan doesn't meet expectations, optimze the query by selecting transformation rules until the final query plan achieves a balance between a low cost value and the fulfillment of user requirements..

    Finally, output the optimzed query together with the rules used in achieving the optimized query.

    You can execute the following actions:
    1) Obtain the cost of the given query, taken as 'origin query plan'.
    2) Select a transformation rule to optimize the query, an API whose name is ended with '_rule' or started with 'enable_or_disable_'.
    3) Give optimization advice (e.g., creating indexes) if failing to optimize the index (such as index/view recommendation, resource reallocation).

    Requirements. 
    1) If an API is successfully called, do not call the same API again; 
    2) Do not use any image in the output; 
    """.format(slow_query)

    test_single(task)