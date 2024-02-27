from multiagents.llms import llm_registry
from multiagents.llms.local_chat_model import LocalChatModel
from multiagents.localized_llms.qwen2_inference import qwen2_local_inference, qwen2_server_inference


@llm_registry.register("qwen2_local")
class QwenLocalChat(LocalChatModel):
    def __init__(self, max_retry: int = 100, **kwargs):
        super().__init__(max_retry=max_retry, **kwargs)
        self.inference = qwen2_local_inference


@llm_registry.register("qwen2_server")
class QwenServerChat(LocalChatModel):
    def __init__(self, max_retry: int = 100, **kwargs):
        super().__init__(max_retry=max_retry, **kwargs)
        self.inference = qwen2_server_inference
