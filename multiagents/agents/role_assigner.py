from __future__ import annotations

import bdb
import re
from string import Template
from typing import TYPE_CHECKING, List

from multiagents.message import RoleAssignerMessage, Message

from multiagents.agents import agent_registry
from multiagents.agents.base import BaseAgent
from multiagents.utils.interact import add_select_message, finish_select_edit_message, user_input, add_display_message

import time

# from multiagents.environments import PipelineEnvironment

@agent_registry.register("role_assigner")
class RoleAssignerAgent(BaseAgent):
    def parse_expert_names(self, reply: str, expert_names: list) -> list:
        selected_names = []
        cleaned_output = reply.strip()
        cleaned_output = re.sub(r"\n+", "\n", cleaned_output)
        cleaned_output = cleaned_output.replace("\n", " ")

        for name in expert_names:
            if name.lower() in cleaned_output.lower():
                selected_names.append(name)
        return selected_names
    
    def parse_strict_expert_names(self, reply: str) -> list:
        selected_names = eval(reply)
        if isinstance(selected_names, list):
            return selected_names
        return []

    
    def user_select_experts(self, selected_names, expert_names):
        if not self.enable_feedback():
            add_display_message('roleAssignment', self.name, 'Selected experts: ' + str(selected_names), time.strftime("%H:%M:%S", time.localtime()))
            return selected_names
        
        if len(selected_names) > 0:
            # print('='*5 + 'SELECTED EXPERTS' + '='*4, flush=True)
            # print(selected_names, flush=True)
            # print('='*25, flush=True)
            if self.language == "zh":
                select_placeholder = '选择的专家: ' + str(selected_names) + '\n\n' + '如果你对已选择的专家满意，请点击\"continue\"。否则请重新选择你更喜欢的专家。'
            else:
                select_placeholder = 'Selected experts: ' + str(selected_names) + '\n\n' + 'If you are satisfied with the selected experts, please click \"continue\". Otherwise, please select the experts you prefer.'
        else:
            if self.language == "zh":
                select_placeholder = '抱歉我们无法选择合适的专家，请手动选择。'
            else:
                select_placeholder = 'We are sorry that we cannot select proper experts. Please manually select the experts.'

        add_select_message('roleAssignment', self.name, select_placeholder, time.strftime("%H:%M:%S", time.localtime()), expert_names)
        experts_reply = user_input(select_placeholder + '\n')
        finish_select_edit_message('roleAssignment', self.name)
        if experts_reply == "" or "continue" in experts_reply.lower():
            return selected_names
        selected_names = self.parse_strict_expert_names(experts_reply)
        return selected_names

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

        selected_names = []
        for i in range(self.max_retry):
            try:
                message = self.llm._construct_messages(prompt)
                self.llm.change_messages(self.role_description, message)
                response = self.llm.parse(role=self.name, task="assign_role")

                selected_names = self.parse_expert_names(response['content'], expert_names=expert_names)
                if selected_names == []:
                    print("no experts are selected")
                    selected_names = []
                    continue
                break
            except (KeyboardInterrupt, bdb.BdbQuit):
                raise
            except Exception as e:
                continue

        selected_names = self.user_select_experts(selected_names, expert_names)
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
