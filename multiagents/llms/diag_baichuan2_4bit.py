from multiagents.llms.local_chat_model import LocalChatModel
from . import llm_registry
import sys
sys.path.append("../../../")
from localized_llms.inference import baichuan2_4bit_inference

@llm_registry.register("diag-baichuan2-4bit")
class DiagBaichuan2_4bitChat(LocalChatModel):
    def __init__(self, max_retry: int = 100, **kwargs):
        super().__init__(max_retry=max_retry, **kwargs)
        self.inference = baichuan2_4bit_inference