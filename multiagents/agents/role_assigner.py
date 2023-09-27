from __future__ import annotations

import asyncio
from colorama import Fore


import bdb
import re
from string import Template
from typing import TYPE_CHECKING, List

from multiagents.message import RoleAssignerMessage, Message

from multiagents.agents import agent_registry
from multiagents.agents.base import BaseAgent

# from multiagents.environments import PipelineEnvironment


@agent_registry.register("role_assigner")
class RoleAssignerAgent(BaseAgent):
    def step(
        self, advice: str, expert_names: list, alert_info: str
    ) -> RoleAssignerMessage:
        # logger.debug("", self.name, Fore.MAGENTA)
        # prompt = self._fill_prompt_template(advice, task_description, cnt_critic_agents)
        # logger.debug(f"Prompt:\n{prompt}", "Role Assigner", Fore.CYAN)
        
        prompt = self.get_all_prompts(
            advice=advice,
            task_description=str(expert_names),
            alert_info=alert_info,
        )

        parsed_response = None
        selected_names = []        
        for i in range(self.max_retry):
            try:
                response = self.llm.generate_response(
                    prompt
                )
                cleaned_output = response.content
                cleaned_output = cleaned_output.strip()
                cleaned_output = re.sub(r"\n+", "\n", cleaned_output)
                cleaned_output = cleaned_output.replace("\n", " ")

                for name in expert_names:
                    if name.lower() in cleaned_output.lower():
                        selected_names.append(name)
                if selected_names == []:
                    print("no experts are selected")
                    selected_names = []
                    continue
                break
            except (KeyboardInterrupt, bdb.BdbQuit):
                raise
            except Exception as e:
                continue

        if selected_names == []:
            raise RuntimeError(f"{self.name} failed to generate valid response.")
 
        # message = RoleAssignerMessage(
        #     content=parsed_response, sender=self.name, sender_agent=self
        # )

        return selected_names



    async def astep(self, env_description: str = "") -> RoleAssignerMessage:
        """Asynchronous version of step"""
        pass

    def _fill_prompt_template(
        self, advice, task_description: str, cnt_critic_agents: int
    ) -> str:
        """Fill the placeholders in the prompt template

        In the role_assigner agent, three placeholders are supported:
        - ${task_description}
        - ${cnt_critic_agnets}
        - ${advice}
        """
        input_arguments = {
            "task_description": task_description,
            "cnt_critic_agents": cnt_critic_agents,
            "advice": advice,
        }
        return Template(self.prompt_template).safe_substitute(input_arguments)

    def add_message_to_memory(self, messages: List[Message]) -> None:
        self.memory.add_message(messages)

    def reset(self) -> None:
        """Reset the agent"""
        self.memory.reset()
        # TODO: reset receiver
