from typing import NamedTuple, Union
from enum import Enum

import abc


class AgentAction(NamedTuple):
    """Agent's action to take."""

    tool: str
    tool_input: Union[str, dict]
    log: str


class AgentFinish(NamedTuple):
    """Agent's return value."""

    return_values: dict
    log: str


class AgentCriticism(NamedTuple):
    """Agent's criticism."""

    is_agree: bool
    criticism: str
    sender_agent: object = None


class AGENT_TYPES(Enum):
    ROLE_ASSIGNMENT = "role_assigner"
    SOLVER = "solver"
    CRITIC = "critic"
    REPORTER = "reporter"
    # EXECUTION = 3
    # EVALUATION = 4
    # MANAGER = 5


class Singleton(abc.ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call method for the singleton metaclass."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
def get_cur_task(task):
    if task in ['expert_root_cause', 'expert_solution']:
        return 'expertDiagnosis'
    
    if task == 'review':
        return 'groupDiscussion'
    
    if task in ['refine_root_cause', 'refine_solution']:
        return 'reportGeneration'
    
    raise ValueError(f'Invalid task: {task}')
