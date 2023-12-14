from multiagents.registry import Registry

llm_registry = Registry(name="LLMRegistry")

from .base import BaseLLM, BaseChatModel, BaseCompletionModel, LLMResult
from .openai import OpenAIChat, OpenAICompletion
# from .diag_llama2 import DiagLlama2Chat
# from .diag_codellama import DiagCodeLlamaChat
# from .diag_baichuan2 import DiagBaichuan2Chat
