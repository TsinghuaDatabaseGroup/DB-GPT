from multiagents.registry import Registry
agent_registry = Registry(name="AgentRegistry")

from .base import BaseAgent
from .conversation_agent import ConversationAgent
# from .tool_agent import ToolAgent

from .role_assigner import RoleAssignerAgent
# from .critic import CriticAgent
# from .evaluator import EvaluatorAgent
from .solver import SolverAgent
from .reporter import ReporterAgent
# from .manager import ManagerAgent
# from .executor import ExecutorAgent
# from .executor_fc import ExecutorAgent_fc