from multiagents.registry import Registry

llm_registry = Registry(name="LLMRegistry")

from .base import BaseLLM, BaseChatModel, BaseCompletionModel, LLMResult
from .openai import OpenAIChat, OpenAICompletion
# from .diag_llama import DiagLlamaChat
