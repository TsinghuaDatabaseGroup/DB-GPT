import logging
import os
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from multiagents.llms.base import LLMResult
from . import llm_registry
from .base import BaseChatModel, BaseCompletionModel, BaseModelArgs
import requests
import json
import aiohttp
import asyncio
import time
import random
import re
from termcolor import colored
from tqdm import tqdm

from openai import OpenAI


def remove_charts(text):
    pattern = r'\[chart\].*?\.html'
    output = re.sub(pattern, '', str(text), flags=re.DOTALL)

    return output


class OpenAIChatArgs(BaseModelArgs):
    model: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=2048)
    temperature: float = Field(default=1.0)
    top_p: int = Field(default=1)
    n: int = Field(default=1)
    stop: Optional[Union[str, List]] = Field(default=None)
    presence_penalty: int = Field(default=0)
    frequency_penalty: int = Field(default=0)


class OpenAICompletionArgs(OpenAIChatArgs):
    model: str = Field(default="text-davinci-003")
    suffix: str = Field(default="")
    best_of: int = Field(default=1)


@llm_registry.register("text-davinci-003")
class OpenAICompletion(BaseCompletionModel):
    args: OpenAICompletionArgs = Field(default_factory=OpenAICompletionArgs)

    def __init__(self, max_retry: int = 100, **kwargs):
        args = OpenAICompletionArgs()
        args = args.dict()
        for k, v in args.items():
            args[k] = kwargs.pop(k, v)
        if len(kwargs) > 0:
            logging.warning(f"Unused arguments: {kwargs}")
        super().__init__(args=args, max_retry=max_retry)

    def generate_response(self, prompt: str) -> LLMResult:

        client = OpenAI( api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
                )

        response = client.completions.create(prompt=prompt, **self.args.dict())
        return LLMResult(
            content=response["choices"][0]["text"],
            send_tokens=response["usage"]["prompt_tokens"],
            recv_tokens=response["usage"]["completion_tokens"],
            total_tokens=response["usage"]["total_tokens"],
        )

    async def agenerate_response(self, prompt: str) -> LLMResult:

        client = OpenAI( api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
                )

        response = await client.completions.create(prompt=prompt, **self.args.dict())
        return LLMResult(
            content=response["choices"][0]["text"],
            send_tokens=response["usage"]["prompt_tokens"],
            recv_tokens=response["usage"]["completion_tokens"],
            total_tokens=response["usage"]["total_tokens"],
        )


@llm_registry.register("gpt-4")
@llm_registry.register("gpt-3.5-turbo")
class OpenAIChat(BaseChatModel):
    args: OpenAIChatArgs = Field(default_factory=OpenAIChatArgs)
    conversation_history: dict = []
    TRY_TIME: int = 1000

    def __init__(self, max_retry: int = 100, **kwargs):
        super().__init__(**kwargs)  # Call the constructor of the base class
        
        args = OpenAIChatArgs()
        args = args.dict()

        self.conversation_history = []
        self.TRY_TIME = 1000

        for k, v in args.items():
            args[k] = kwargs.pop(k, v)
        if len(kwargs) > 0:
            logging.warning(f"Unused arguments: {kwargs}")
        super().__init__(args=args, max_retry=max_retry)

    def _construct_system_messages(self, prompt: str):
        return [{"role": "system", "content": prompt}]

    def _construct_messages(self, prompt: str):
        return [{"role": "user", "content": prompt, "time": time.strftime("%H:%M:%S", time.localtime())}]

    def change_messages(self, role_description, messages):

        if role_description != "":
            role_message = self._construct_system_messages(role_description)
            self.conversation_history = role_message + messages
        else:
            self.conversation_history = messages

    def parse(self):
        #messages = self._construct_messages(prompt) # TODO add history messages

        training_data_position = "./alert_results/logs/diag_training_data_11_27.jsonl"
        client = OpenAI( api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
                )
        self.args.model = "gpt-4-0613"

        messages = self.conversation_history

        new_messages = []

        for message in messages:
            new_message = message
            # pop the time key-value from the message
            if "time" in new_message:
                new_message.pop("time")
            if new_message["role"] == "function":
                new_message["role"] = "assistant"
            new_messages.append(new_message)
        messages = new_messages

        for i in range(self.TRY_TIME):
            
            try:
                response = client.chat.completions.create(
                    messages=messages,
                    **self.args.dict()
                )   
                try:
                    output = response.choices[0].message.content
                except:
                    output = None

                if output is None:
                    return {"role": "assistant", "content": "OpenAI service is unavailable. Please try again.", "time": time.strftime("%H:%M:%S", time.localtime())}

                output = remove_charts(output)

                '''
                with open(training_data_position, "a") as wf:
                    if isinstance(messages, list):
                        messages_str = messages # messages[-1]
                        if isinstance(messages_str, dict):
                            messages_str = str(messages_str["content"])
                        else:
                            messages_str = str(messages_str)
                    else:
                        if isinstance(messages, dict):
                            messages_str = str()
                        else:
                            messages_str = str(messages)

                    # messages_str = messages_str.replace('\n', '\\n')
                    # messages_str = messages_str.replace('"', '\\"')

                    # output = output.replace('\n', '\\n')
                    # output = output.replace('"', '\\"')

                    messages_str = remove_charts(messages_str)

                    # dump into the json file in pretty format
                    json.dump({"input": str(messages_str), "output": str(output)}, wf)
                    # add \n at the end of the line
                    wf.write('\n')                
                '''

                return {"role": "assistant", "content": output, "time": time.strftime("%H:%M:%S", time.localtime())}
            except:
                print(f"Generate_response Exception. Try again.")

                # if i !=0 and i%10 == 0:
                #     # randomly read a line from openai_keys.txt file (key pool)
                #     if os.path.exists('openai_keys.txt'):

                #         with open('openai_keys.txt', 'r') as f:
                #             lines = f.readlines()
                #             rowid = random.randint(0, len(lines)-1)
                #             line = lines[rowid].strip()
                #             items = line.split(" ")

                #             while items[0] == openai.api_key:
                #                 rowid = random.randint(0, len(lines)-1)
                #                 line = lines[rowid].strip()
                #                 items = line.split(" ")

                #             openai.api_key = items[0]
                #             # if len(items) == 1:
                #             #     openai.organization = ""
                #             # else:
                #             #     openai.organization = items[1]

                #             # print(f"[{str(rowid)}] openai key changed to {api_key}")
                #             # if i%100 == 0:
                #             #     print(colored(f"{messages}", "red"))

                #             f.close()
                time.sleep(min(i**2, 60))
                continue

        return {"role": "assistant", "content": "OpenAI service is unavailable. Please try again."}


    def generate_response(self, prompt: str) -> LLMResult:
        messages = self._construct_messages(prompt)

        client = OpenAI( api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
                )
        self.args.model = "gpt-4-0613"

        for i in range(self.TRY_TIME):
            try:
                response = client.chat.completions.create(
                    messages=messages, **self.args.dict()
                )
            except :
                print(f"Generate_response Exception. Try again.")
                time.sleep(.5)

                if i !=0 and i%10 == 0:
                    # randomly read a line from openai_keys.txt file as the openai key
                    with open('openai_keys.txt', 'r') as f:
                        lines = f.readlines()
                        rowid = random.randint(0, len(lines)-1)
                        line = lines[rowid].strip()
                        items = line.split(" ")

                        while items[0] == client.api_key:
                            rowid = random.randint(0, len(lines)-1)
                            line = lines[rowid].strip()
                            items = line.split(" ")

                        client.api_key = items[0]
                        if len(items) == 1:
                            client.organization = ""
                        else:
                            client.organization = items[1]

                        # print(f"[{str(rowid)}] openai key changed to {openai.api_key}")
                        # if i%100 == 0:
                        #     print(colored(f"{messages}", "red"))

                        f.close()
                else:
                    time.sleep(1)

                continue

            return LLMResult(
                content=response["choices"][0]["message"]["content"],
                send_tokens=response["usage"]["prompt_tokens"],
                recv_tokens=response["usage"]["completion_tokens"],
                total_tokens=response["usage"]["total_tokens"],
            )

    async def agenerate_response(self, prompt: str) -> LLMResult:
        messages = self._construct_messages(prompt)

        client = OpenAI( api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
                )
        self.args.model = "gpt-4-0613"

        for _ in range(self.TRY_TIME):
            try:
                response = await client.chat.completions.create(
                    messages=messages, **self.args.dict()
                )
            except:
                raise
            return LLMResult(
                content=response["choices"][0]["message"]["content"],
                send_tokens=response["usage"]["prompt_tokens"],
                recv_tokens=response["usage"]["completion_tokens"],
                total_tokens=response["usage"]["total_tokens"],
            )