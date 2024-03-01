from multiagents.llms import llm_registry
from multiagents.llms.local_chat_model import LocalChatModel, remove_charts
from multiagents.localized_llms.qwen2_inference import qwen2_local_inference, qwen2_server_inference
import time


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

    def parse(self):
        messages = self.conversation_history

        new_messages = []
        for message in messages:
            # pop the time key-value from the message
            if "time" in message:
                message.pop("time")
            if message["role"] in ('system', 'user', 'assistant'):
                new_messages.append(message)
            else:
                assert message['role'] == "function" and new_messages[-1]['role'] == "assistant"
                new_messages[-1]['content'] += f"\nObservation: {message['content']}"

        output = self.inference.inference(new_messages)

        output = remove_charts(output)
        # import pdb; pdb.set_trace()
        return {"role": "assistant", "content": output, "time": time.strftime("%H:%M:%S", time.localtime())}