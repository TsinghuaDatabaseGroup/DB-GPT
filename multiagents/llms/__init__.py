from multiagents.registry import Registry

llm_registry = Registry(name="LLMRegistry")

from .base import BaseLLM, BaseChatModel, BaseCompletionModel, LLMResult
from .openai import OpenAIChat, OpenAICompletion
from .diag_baichuan2_4bit import DiagBaichuan2_4bitChat
from .diag_baichuan2 import DiagBaichuan2Chat
from .diag_codellama import DiagCodeLlamaChat
from .diag_llama2 import DiagLlama2Chat
from .qwen_vllm import QwenVllmChat
from .feedback_openai import FeedbackOpenAIChat
from .feedback_qwen import FeedbackQwenChat
