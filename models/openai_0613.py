
import ast
import concurrent
from csv import writer
import json
import openai
import os
import pandas as pd
import requests
from scipy import spatial
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken
from tqdm import tqdm
from termcolor import colored
import time

from pprint import pprint
import pdb

class chatgpt_0613:
    def __init__(self):
        self.conversation_history = []
        self.time = time.time()
        self.TRY_TIME = 3

    def add_message(self, message):
        self.conversation_history.append(message)

    def change_messages(self,messages):
        self.conversation_history = messages

    def display_conversation(self, detailed=False):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        print("before_print"+"*"*50)
        for message in self.conversation_history:
            print_obj = f"{message['role']}: {message['content']} "
            if "function_call" in message.keys():
                print_obj = print_obj + f"function_call: {message['function_call']}"
            print_obj += ""
            print(
                colored(
                    print_obj,
                    role_to_color[message["role"]],
                )
            )
        print("end_print"+"*"*50)

    def cut_history(self):
        ptr = 0
        # while len(str(self.conversation_history[ptr:])) > 5000:
        #     ptr += (len(self.conversation_history) - ptr) // 2
        #
        # if ptr != 0:
        #     print("Cut history !!!!!!!!!!!!!!!!!!!!")
        return ptr

    def parse(self,functions,**args):
        # while time.time() - self.time < 3: #最短间隔3s
        #     continue
        self.time = time.time()
        
        # function name超出64字符长度的需要做一步映射，不然会报错
        func_name_map = {}
        for function_dict in functions:
            function_name = function_dict["name"]
            if len(function_name) >= 64:
                cut_func_name = function_name[:64]
                func_name_map[cut_func_name] = function_name
                function_dict["name"] = cut_func_name
            else:
                func_name_map[function_name] = function_name
        conversation_history = self.conversation_history[self.cut_history():]
        for _ in range(self.TRY_TIME):
            json_data = openai.ChatCompletion.create(
                # self.conversation_history, functions=functions,**args
                model="gpt-3.5-turbo-16k-0613", 
                messages=conversation_history, 
                functions=functions, 
                max_tokens=1024,
                frequency_penalty=0,
                presence_penalty=0,
                **args
            )

            try:
                # print(f"total tokens: {json_data['usage']['total_tokens']}")
                pdb.set_trace()
                message = json_data["choices"][0]["message"]
                if "function_call" in message:
                    function_call = message["function_call"]
                    function_call["name"] = func_name_map[function_call["name"]]
                return message
            except BaseException as e:
                print(f"Parsing Exception: {repr(e)}. Try again.")
                if json_data is not None:
                    print(f"OpenAI return: {json_data}")
                # pdb.set_trace()
                continue

        return {"role": "assistant", "content": "OpenAI service is unavailable. Please try again."}

if __name__ == "__main__":

    # output = '''{"id":"chatcmpl-7Tua9U0LcQPNEjGEFetG3SsO4k1nQ","object":"chat.completion","created":1687363369,"model":"gpt-3.5-turbo-16k-0613","choices":[{"index":0,"message":{"role":"assistant","content":"First, I will try to combine 1 and 2 to see if it equals 24.","function_call":{"name":"play_24","arguments":"{\n  \"input\": \"1*2=2\"\n}"}},"finish_reason":"function_call"}],"usage":{"prompt_tokens":503,"completion_tokens":41,"total_tokens":544}}'''
    # output = output.replace('\n', '\\n')
    # output = output.replace('\"', '\\"')
    # json.loads(r'{}'.format(output),strict=False)
    # exit()
    llm = chatgpt_0613()
    messages = [
        {'role': 'system', 'content': '''You are AutoGPT, you can use many tools(functions) to do
the following task.\nFirst I will give you the task description, and your task start.\nAt each step, you need to give your thought to analyze the status now and what to do next, with a function call to actually excute your step.\nAfter the call, you will get the call result, and you are now in a new state.\nThen you will analyze your status now, then decide what to do next...\nAfter many (Thought-call) pairs, you finally perform the task, then you can give your finial answer.\nRemember: \n1.the state change is , you can\'t go
back to the former state, if you want to restart the task, say "I give up and restart".\n2.All the thought is short, at most in 5 sentence.\nLet\'s Begin!\nTask description: Use numbers and basic arithmetic operations (+ - * /) to obtain exactly one number=24. Each
step, you are only allowed to choose two of the left numbers to obtain a new number. For example, you can combine [3,13,9,7] as 7*9 - 3*13 = 24.\nRemember:\n1.all of the number must be used , and must be used ONCE. So Only when left numbers is exact 24, you will win. So you don\'t succeed when left number = [24, 5]. You succeed when left number = [24]. \n2.all the try takes exactly 3 steps, look
at the input format'''}, 
{'role': 'user', 'content': '\nThe real task input is: [1, 2, 4, 7]\nBegin!\n'}
]
    functions = [{'name': 'play_24', 'description': '''make your current conbine with the format "x operation y = z (left: aaa) " like "1+2=3, (left: 3 5 7)", then I will tell you whether you win. This is the ONLY way
to interact with the game, and the total process of a input use 3 steps of call, each step you can only combine 2 of the left numbers, so the count of left numbers decrease from 4 to 1''','parameters':{'type': 'object', 'properties':{}}}]#, 'parameters': {'type': 'object', 'properties': {'input': {'type': 'string', 'description': 'describe what number you want to conbine, and how to conbine.'}}, 'required': ['input']}}]

    llm.change_messages(messages)
    output = llm.parse(functions=functions)
    print(output)