import logging
from abc import abstractmethod
from typing import List, NamedTuple, Set, Union

from pydantic import BaseModel, Field

from multiagents.llms import BaseLLM
from multiagents.memory import BaseMemory, ChatHistoryMemory
from multiagents.message import Message
from multiagents.custom_parser import OutputParser
from string import Template


class BaseAgent(BaseModel):
    name: str
    llm: BaseLLM
    output_parser: OutputParser
    prompt_template: str = Field(default="")
    role_description: str = Field(default="")
    memory: BaseMemory = Field(default_factory=ChatHistoryMemory)
    max_retry: int = Field(default=3)
    receiver: Set[str] = Field(default=set({"all"}))
    async_mode: bool = Field(default=True)
    language: str = Field(default="en")
    knowledge_list: list = Field(default=[])

    @abstractmethod
    def step(self, env_description: str = "") -> Message:
        """Get one step response"""
        pass

    @abstractmethod
    def astep(self, env_description: str = "") -> Message:
        """Asynchronous version of step"""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the agent"""
        pass

    @abstractmethod
    def add_message_to_memory(self, messages: List[Message]) -> None:
        """Add a message to the memory"""
        pass

    def get_all_prompts(self, **kwargs):
        prompt = Template(self.prompt_template).safe_substitute(
            **kwargs
        )

        return prompt

    def get_receiver(self) -> Set[str]:
        return self.receiver

    def set_receiver(self, receiver: Union[Set[str], str]) -> None:
        if isinstance(receiver, str):
            self.receiver = set({receiver})
        elif isinstance(receiver, set):
            self.receiver = receiver
        else:
            raise ValueError(
                "input argument `receiver` must be a string or a set of string"
            )

    def add_receiver(self, receiver: Union[Set[str], str]) -> None:
        if isinstance(receiver, str):
            self.receiver.add(receiver)
        elif isinstance(receiver, set):
            self.receiver = self.receiver.union(receiver)
        else:
            raise ValueError(
                "input argument `receiver` must be a string or a set of string"
            )

    def remove_receiver(self, receiver: Union[Set[str], str]) -> None:
        if isinstance(receiver, str):
            try:
                self.receiver.remove(receiver)
            except KeyError as e:
                logging.warning(f"Receiver {receiver} not found.")
        elif isinstance(receiver, set):
            self.receiver = self.receiver.difference(receiver)
        else:
            raise ValueError(
                "input argument `receiver` must be a string or a set of string"
            )
        
    def enable_feedback(self):
        return self.llm is not None and hasattr(self.llm, 'enable_feedback') and self.llm.enable_feedback