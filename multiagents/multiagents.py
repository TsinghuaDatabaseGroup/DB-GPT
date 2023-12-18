import asyncio
import logging
from typing import List

from multiagents.agents.conversation_agent import BaseAgent
from multiagents.environments.base import BaseEnvironment
from multiagents.environments import DBAEnvironment
from multiagents.initialization import load_agent, load_environment, prepare_task_config
from utils.utils import AGENT_TYPES
from multiagents.tools.metrics import get_workload_statistics

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)

class MultiAgents:
    def __init__(self, agents: List[BaseAgent], environment: BaseEnvironment):
        
        self.agents = agents
        self.environment = environment

    @classmethod
    def from_task(cls, task, args):
        
        # Prepare the config of the task
        task_config = prepare_task_config(task, args)
        model_type = task_config['llm_type']

        # Build the agents
        reporter = None
        agents = {}
        for agent_config in task_config["agents"]:
            
            agent_type = AGENT_TYPES(agent_config["agent_type"])
            agent_type_name = agent_config["agent_type"]

            agent = load_agent(agent_config)

            if agent_type_name == "reporter":
                reporter = agent
            else:
                if agent_type not in agents:
                    agents[agent_type] = [agent]
                else:
                    agents[agent_type].append(agent)

        if reporter is None:
            raise ValueError("Reporter is not specified.")

        # Build the environment
        env_config = task_config["environment"]
        env_config["agents"] = agents
        env_config["reporter"] = reporter
        env_config["task_description"] = task_config.get("task_description", "")

        environment: DBAEnvironment = load_environment(env_config)
        
        return cls(agents, environment), model_type

    async def run(self, args):
        """Run the environment from scratch"""
        self.environment.reset()

        report, records = await self.environment.step(args)
        
        return report, records

    def reset(self):
        self.environment.reset()
        for agent in self.agents:
            agent.reset()

    def next(self, *args, **kwargs):
        """Run the environment for one step and return the return message."""
        return_message = asyncio.run(self.environment.step(*args, **kwargs))
        return return_message

    def submit(self, message):
        """Submit a message to the environment and return the return message."""
        return_message = asyncio.run(self.environment.submit(message))
        return return_message