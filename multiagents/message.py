from pydantic import BaseModel, Field
from typing import List, Tuple, Set, Union
from multiagents.utils.utils import AgentAction

class Message(BaseModel):
    content: dict = Field(default={"diagnose": "", "solution": [], "knowledge": ""})
    sender: str = Field(default="")
    receiver: Set[str] = Field(default=set({"all"}))
    tool_response: List[Tuple[AgentAction, str]] = Field(default=[])

class SolverMessage(Message):
    pass


class CriticMessage(Message):
    review: str


class ExecutorMessage(Message):
    pass


class EvaluatorMessage(Message):
    score: Union[bool, List[bool], int, List[int]]
    advice: str = Field(default="")


class RoleAssignerMessage(Message):
    pass
