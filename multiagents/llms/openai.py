import json
import logging
import os
from typing import List, Optional, Union
from pydantic import Field

from configs import ONLINE_LLM_MODEL
from multiagents.llms.base import LLMResult
from . import llm_registry
from .base import BaseChatModel, BaseCompletionModel, BaseModelArgs
import time
import random
import re
from openai import OpenAI
import openai
from multiagents.utils.interact import add_display_message
from multiagents.utils.utils import get_cur_task


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
    client: None = None

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

        assert not openai.__version__.startswith('0.')
        api_kwargs = {}
        api_key = ONLINE_LLM_MODEL["openai-api"].get("api_key", None)
        api_base = ONLINE_LLM_MODEL["openai-api"].get("api_base_url", None)
        if api_base:
            api_kwargs['base_url'] = api_base
        if api_key:
            api_kwargs['api_key'] = api_key
        self.client = openai.OpenAI(**api_kwargs)


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

    def parse(self, role="", task=""):
        #messages = self._construct_messages(prompt) # TODO add history messages
        self.args.model = ONLINE_LLM_MODEL["openai-api"]["model_name"]
        messages = self.conversation_history

        new_messages = []

        for message in messages:
            new_message = message
            # pop the time key-value from the message
            if "time" in new_message:
                new_message.pop("time")
            # openai最新版如果role是function，必须有name(函数名)
            if new_message["role"] == "function":
                new_message["role"] = "assistant"
            new_messages.append(new_message)
        messages = new_messages

        output = 'OpenAI service is unavailable. Please try again.'

        for i in range(self.TRY_TIME):
            
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    **self.args.dict()
                )   
                try:
                    output = response.choices[0].message.content

                    # 保存所有原始调用记录以便debug
                    # saved_msgs = messages + [{'role': "assistant", "content": output}]
                    # if not os.path.exists(r"saved_msg_gpt4"):
                    #     os.mkdir(r"saved_msg_gpt4")
                    # with open(f"saved_msg_gpt4/msg_{time.strftime('%H_%M_%S', time.localtime())}.json", "w", encoding='utf8') as f:
                    #     json.dump(saved_msgs, f, ensure_ascii=False, indent=4)
                except:
                    pass

                if output is not None:
                    output = remove_charts(output)

                break
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

        cur_time = time.strftime("%H:%M:%S", time.localtime())

        if not self.enable_feedback and task in ['expert_root_cause', 'expert_solution', 'review', 'refine_root_cause', 'refine_solution']:
            add_display_message(get_cur_task(task), role, output, cur_time)

        return {"role": "assistant", "content": output, "time": cur_time}

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
        
def call_openai(messages):
    call_openai.chat.change_messages("", messages)
    reply = call_openai.chat.parse()
    return reply['content']
call_openai.chat = OpenAIChat()