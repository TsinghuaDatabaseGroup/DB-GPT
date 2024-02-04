from multiagents.llms.local_chat_model import LocalChatModel
from . import llm_registry
from multiagents.localized_llms.inference import codellama_inference

@llm_registry.register("diag-codellama")
class DiagCodeLlamaChat(LocalChatModel):
    def __init__(self, max_retry: int = 100, **kwargs):
        super().__init__(max_retry=max_retry, **kwargs)
        self.inference = codellama_inference