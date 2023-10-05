from __future__ import annotations

import asyncio
from colorama import Fore
import re
import bdb
import time
import logging
import json
from string import Template
from pydantic import Field
from typing import TYPE_CHECKING, List, Tuple
from termcolor import colored

# from multiagents.environments import PipelineEnvironment
from multiagents.message import SolverMessage, Message, CriticMessage
from multiagents.memory import BaseMemory, ChatHistoryMemory
from multiagents.agents import agent_registry
from multiagents.agents.base import BaseAgent
from multiagents.utils.utils import AgentCriticism
from multiagents.tools.api_retrieval import APICaller
from multiagents.reasoning_algorithms import UCT_vote_function, node_to_chain
from multiagents.utils.utils import AgentAction, AgentFinish
from multiagents.reasoning_algorithms import base_env
from prompt_templates.Report_prompts import  ANOMALY_DESC_PROMPT

@agent_registry.register("reporter") # solver is also tool agent by default
class ReporterAgent(BaseAgent):
    class Config:
        arbitrary_types_allowed = True

    verbose: bool = Field(default=False)
    name: str = Field(default="ChiefDBA")
    max_history: int = 3
    alert_str: str = ""
    alert_dict: dict = {}
    anomaly_desc_prompt: str = ANOMALY_DESC_PROMPT

    report: dict = {"anomaly date": "", "anomaly description": "", "root cause": "", "diagnosis process": "", "solutions": ""}

    def initialize_report(self):

        seconds = int(self.alert_dict['start_time'])
        start_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))
        self.report["anomaly date"] = start_date

        anomaly_desc_prompt = self.anomaly_desc_prompt.replace("{anomaly_str}", self.alert_str)

        anomaly_desc = self.llm.generate_response(anomaly_desc_prompt).content
        
        self.report["anomaly description"] = anomaly_desc


    async def step(
        self, former_solution: str, advice: str, task_description: str = "", **kwargs
    ) -> SolverMessage:
        
        # prompt = self._fill_prompt_template(
        #     former_solution, critic_opinions, advice, task_description
        # )
        # try to find the diagnosis steps based on the identified alerts
        
        # tool_observation = [self.tool_memory.to_string()] # get the results of using tools
        # prompt = self._fill_prompt_template(task_description, tool_observation)
        
        # prompt = self.get_all_prompts(
        #     advice=advice,
        #     task_description=task_description,
        #     role_description=self.role_description,
        #     **kwargs,
        # )
        # parsed_response = self.output_parser.parse()

        # Step1: configure attirbutes in the tasksolving environment
        
        chain = UCT_vote_function(agent_name=self.name, prompt_template=self.prompt_template, llm=self.llm,env=tasksolving_env, output_parser=self.output_parser, alert_dict=self.alert_dict, alert_str=self.alert_str, agent=self)

        result_node = chain.start(simulation_count=2,epsilon_new_node=0.3,choice_count=1,vote_candidates=2,vote_count=1,single_chain_max_step=10)

        # result_node.messages
        # result_node.description

        # print(colored(f"start analysis ({self.name})", "green")) # role 
        # for i in range(self.max_retry):
        #     try:
        #         time.sleep(.1)
        #         response = self.llm.generate_response(prompt) # new node (terminal conditon: the action is speak)
        #         # chain = UCT_vote_function(llm=self.llm,env=env)
                
        #         parsed_response = self.output_parser.parse(response)
        #         if isinstance(parsed_response, AgentAction):
        #             # If the response is an action, call the tool
        #             # and append the observation to tool_observation
        #             observation, status = tasksolving_env.step(parsed_response)
                    
        #             tool_observation.append(
        #                 parsed_response.log.strip()
        #                 + f"\nObservation: {str(observation).strip()}"
        #             )
        #         break
        #     except BaseException as e:
        #         logging.error(e)
        #         logging.warning("Retrying...")
        #         continue
        
        # history = self.memory.to_messages(self.name, start_index=-self.max_history)
        # print(colored(f"end analysis ({self.name})", "green")) # role 

        # for i in range(self.max_retry):
        #     try:
        #         response = self.llm.generate_response(
        #             prompt
        #         )
        #         parsed_response = self.output_parser.parse(response)
        #         break
        #     except (KeyboardInterrupt, bdb.BdbQuit):
        #         raise
        #     except Exception as e:
        #         continue

        # adopt tree of thought here

        message = {
            "content": ""
            if result_node.messages is None
            else result_node.messages[-1],
            "sender": self.name,
            "receiver": self.get_receiver()
        }

        # message = SolverMessage(
        #     content={"diagnose": "", "solution": [], "knowledge": ""}
        #     if result_node.messages is None
        #     else result_node.messages[-1],
        #     sender=self.name,
        #     receiver=self.get_receiver()
        # )

    # content: dict = Field(default={"diagnose": "", "solution": [], "knowledge": ""})
    # sender: str = Field(default="")
    # receiver: Set[str] = Field(default=set({"all"}))
    # tool_response: List[Tuple[AgentAction, str]] = Field(default=[])

        return message

    async def astep(self, env_description: str = "") -> SolverMessage:
        """Asynchronous version of step"""
        pass

    def _fill_prompt_template(
        self, env_description: str = "", tool_observation: List[str] = []) -> str:
        
        """Fill the placeholders in the prompt template

        In the tool agent, these placeholders are supported:
        - ${agent_name}: the name of the agent
        - ${env_description}: the description of the environment
        - ${role_description}: the description of the role of the agent
        - ${chat_history}: the chat history of the agent
        - ${tools}: the list of tools and their usage
        - ${tool_names}: the list of tool names
        - ${tool_observations}: the observation of the tool in this turn
        """
        #retriever = api_retriever()        
        #relevant_tools = retriever.query(Template(self.prompt_template).safe_substitute({"chat_history": self.memory.to_string(add_sender_prefix=True)}), self.tools)
        
        tools = "\n".join([f"> {tool}: {self.tools.functions[tool]['desc']}" for tool in self.tools.functions])
        tools = tools.replace("{{", "{").replace("}}", "}")
        tool_names = ", ".join([tool for tool in self.tools.functions])
        if self.alert_dict['start_time'] != "":
            input_arguments = {
                "alert_info": self.alert_str,
                "agent_name": self.name,
                "env_description": env_description,                                 
                "role_description": self.role_description,
                "chat_history": self.memory.to_string(add_sender_prefix=True),
                "tools": tools,
                "tool_names": tool_names,
                "tool_observation": "\n".join(tool_observation),
            }
        else:
            input_arguments = {
                "agent_name": self.name,
                "env_description": env_description,                                 
                "role_description": self.role_description,
                "chat_history": self.memory.to_string(add_sender_prefix=True),
                "tools": tools,
                "tool_names": tool_names,
                "tool_observation": "\n".join(tool_observation),
             }

        return Template(self.prompt_template).safe_substitute(input_arguments)
    
    def add_message_to_memory(self, messages: List[Message]) -> None:
        self.memory.add_message(messages)

    def reset(self) -> None:
        """Reset the agent"""
        self.memory.reset()
        # TODO: reset receiver        