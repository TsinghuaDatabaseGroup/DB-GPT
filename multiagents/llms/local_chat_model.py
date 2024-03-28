from typing import List
from multiagents.llms.base import LLMResult
from .base import BaseChatModel, BaseCompletionModel, BaseModelArgs
import time
import re

def remove_charts(text):
    pattern = r'\[chart\].*?\.html'
    output = re.sub(pattern, '', str(text), flags=re.DOTALL)

    return output

class LocalChatModel(BaseChatModel):
    conversation_history: List = []
    inference: object

    def __init__(self, max_retry: int = 100, **kwargs):
        super().__init__(max_retry = max_retry, **kwargs)  # Call the constructor of the base class
        

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
        messages = self.conversation_history

        new_messages = []
        for message in messages:
            # pop the time key-value from the message
            if "time" in message:
                message.pop("time")
            role = message["role"]
            if role == "function":
                role = "assistant"
            new_messages.append({"role": role, "content": self.inference.preprocess(message["content"])})
        
        new_messages = self.inference.refine_messages(new_messages, task=task)
        
        output = self.inference.inference(new_messages)

        output = remove_charts(output)
        # import pdb; pdb.set_trace()
        return {"role": "assistant", "content": output, "time": time.strftime("%H:%M:%S", time.localtime())}
    
    def generate_response(self, prompt: str) -> LLMResult:
        AssertionError

    async def agenerate_response(self, prompt: str) -> LLMResult:
        AssertionError