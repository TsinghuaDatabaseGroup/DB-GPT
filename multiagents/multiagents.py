import asyncio
import logging
from typing import List

from multiagents.agents.conversation_agent import BaseAgent
from multiagents.environments.base import BaseEnvironment
from multiagents.environments import DBAEnvironment
from multiagents.initialization import load_agent, load_environment, prepare_task_config
from multiagents.utils.utils import AGENT_TYPES
from server.knowledge_base.kb_doc_api import fetch_expert_kb_names


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
        agent_templates = task_config["agents"]
        model_type = task_config['llm_type']
        agents = {}

        # Reporter
        reporter = load_agent(agent_templates[0])
        
        # Assigner for expert selection
        agents[AGENT_TYPES("role_assigner")] = [load_agent(agent_templates[1])]

        # Candidate experts
        expert_names = fetch_expert_kb_names()

        print(f'<flow>{{"title": "初始化专家角色", "content": "初始化的专家为：{"、".join(expert_names)}", "isCompleted": 1, "isRuning": 0}}</flow>')

        for expert_name in expert_names:
            agent_type_name = "solver"
            agent_type = AGENT_TYPES(agent_type_name)

            # copy a new agent_templates[2]
            
            agent_args = agent_templates[2].copy()

            agent_args['name'] = agent_args['name'].replace("${agent_name}", expert_name)
            agent_args['role_description'] = agent_args['role_description'].replace("${agent_name}", expert_name)
            agent_args['prompt_template'] = agent_args['prompt_template'].replace("${agent_name}", expert_name)
                        
            if agent_type not in agents:
                agents[agent_type] = [load_agent(agent_args)]
            else:
                agents[agent_type].append(load_agent(agent_args))

        '''
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
        '''

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