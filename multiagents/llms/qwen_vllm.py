import openai
from multiagents.llms import llm_registry
from multiagents.llms.base import BaseChatModel
import time
from configs import ONLINE_LLM_MODEL
from typing import List, Dict
import os
import re
import json


def remove_charts(text):
    pattern = r'\[chart\].*?\.html'
    output = re.sub(pattern, '', str(text), flags=re.DOTALL)

    return output


@llm_registry.register("qwen1.5_vllm")
class QwenVllmChat(BaseChatModel):
    conversation_history: List = []
    client: None = None
    model_name_or_path: str = "Qwen1.5-14B-Chat"
    generate_cfg: Dict = {'stop': ['Observation:', 'Observation:\n'], 'temperature': 0}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import openai

        assert not openai.__version__.startswith('0.')
        api_kwargs = {}
        api_key = ONLINE_LLM_MODEL["qwen1.5-vllm"].get("api_key", None)
        api_base = ONLINE_LLM_MODEL["qwen1.5-vllm"].get("api_base_url", None)
        if api_base:
            api_kwargs['base_url'] = api_base
        if api_key:
            api_kwargs['api_key'] = api_key

        self.client = openai.OpenAI(**api_kwargs)
        self.model_name_or_path = ONLINE_LLM_MODEL["qwen1.5-vllm"].get("model_name", None)
        self.generate_cfg.update(kwargs)

    @staticmethod
    def _construct_system_messages(prompt: str):
        return [{"role": "system", "content": prompt}]

    @staticmethod
    def _construct_messages(prompt: str):
        return [{"role": "user", "content": prompt, "time": time.strftime("%H:%M:%S", time.localtime())}]

    def change_messages(self, role_description, messages):

        if role_description != "":
            role_message = self._construct_system_messages(role_description)
            self.conversation_history = role_message + messages
        else:
            self.conversation_history = messages

    def parse(self):
        messages = self.conversation_history

        new_messages = []
        for message in messages:
            # pop the time key-value from the message
            if "time" in message:
                message.pop("time")
            if message["role"] in ('system', 'user', 'assistant'):
                new_messages.append(message)
            # else:
            #     assert (
            #             message['role'] == "function" and
            #             new_messages[-1]['role'] == "assistant" and
            #             "Observation:" not in new_messages[-1]['content']
            #     )
            #     new_messages[-1]['content'] += f"\nObservation: {message['content']}"

        output = self.chat(new_messages)
        output = remove_charts(output)
        return {"role": "assistant", "content": output, "time": time.strftime("%H:%M:%S", time.localtime())}

    def chat(self, messages, **kwargs):
        generate_cfg = self.generate_cfg.copy()
        generate_cfg.update(kwargs)

        response = self.client.chat.completions.create(
            model=self.model_name_or_path,
            messages=messages,
            **generate_cfg
        )

        output = response.choices[0].message.content

        if not os.path.exists(r"saved_msg_qwen"):
            os.mkdir(r"saved_msg_qwen")
        saved_msgs = messages + [{'role': "assistant", "content": output}]
        with open(f"saved_msg_qwen/msg_{time.strftime('%H_%M_%S', time.localtime())}.json",
                  "w", encoding='utf8') as f:
            json.dump(saved_msgs, f, ensure_ascii=False, indent=4)

        return output

    def generate_response(self, prompt: str):
        raise AssertionError

    async def agenerate_response(self, prompt: str):
        raise AssertionError
