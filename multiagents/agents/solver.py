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
from tqdm import tqdm

# from multiagents.environments import PipelineEnvironment
from multiagents.message import SolverMessage, Message, CriticMessage
from multiagents.memory import BaseMemory, ChatHistoryMemory
from multiagents.agents import agent_registry
from multiagents.agents.base import BaseAgent
from utils.utils import AgentCriticism
from multiagents.tools.api_retrieval import APICaller
from multiagents.reasoning_algorithms import UCT_vote_function, node_to_chain
from utils.utils import AgentAction, AgentFinish
from multiagents.reasoning_algorithms import base_env

from multiagents.tools.retriever import api_matcher

class ToolNotExistError(BaseException):

    """Exception raised when parsing output from a command fails."""

    def __init__(self, tool_name=""):
        self.tool_name = tool_name

    def __str__(self):
        return f"Tool {self.tool_name} does not exist."


class wrap_tasksolving_env(base_env):
    def __init__(self, task_description, tools, tool_memory):
        super(wrap_tasksolving_env, self).__init__()

        # tool_name, tool_url = 'database',  "http://127.0.0.1:8079/tools/database/"
        # tool_name, tool_config = load_single_tools(tool_name, tool_url)

        # self.tool, _ = import_all_apis(tool_config)

        self.task_description = task_description
        self.tool = tools
        self.tool_memory = tool_memory

        # self.input_description = "The followings are the names of the valid actions:\n"
        self.tool_names = []

        for api in self.tool.functions:
            # self.input_description += api + "\n"
            self.tool_names.append(api)
        self.tool_names.append("finish")

        # for api in self.tool:
        #     func_name = api.name
        #     func_description = api.description

        #     function = {
        #         "name": func_name,
        #         "description": func_description,
        #         "parameters": {
        #             "type": "object",
        #             "properties": {},
        #             "required": []
        #         },
        #     }

        #     param_string = pattern_1.findall(func_description)

        #     for i in param_string:
        #         result = pattern_2.findall(i)[0]
        #         param_name, param_type = result[0], result[1]

        #         param = {
        #             param_name: {
        #                 "type": param_type,
        #                 "description": "", # TODO
        #             }
        #         }

        #         function["parameters"]["properties"].update(param)

        #     self.functions.append(function)

        # self.finish_func = {
        #     "name": "Finish",
        #     "description": "If you think you get the result which can answer the input description, call this function to give the final answer",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "answer": {
        #                 "type": "string",
        #                 "description": "The final answer you want to give the user"
        #             },
        #         },
        #         "required": ["answer"]
        #     }
        # }

        # self.functions.append(self.finish_func)

        self.restart()

    def check_success(self, message):

        if "\"solution\"" in message['content'].lower():
            self.status = 1
        else:
            self.status = 0

        return self.status

    def to_json(self):
        return {}

    def restart(self):
        self.status = 0

    def get_score(self):

        return 0.0


    def step(self, parsed_response=""):
            
        if parsed_response.tool == "Final Answer" or "finish" in parsed_response.tool.lower():
            self.status = 1
            return "", 1

        parameters = json.loads(parsed_response.tool_input)
        observation = self.tool.call_function(parsed_response.tool, **parameters)

        return observation, 0

        # if self.name_to_tool_map.get(action_name):
        #     observation = self.name_to_tool_map[action_name].run(
        #         action_input
        #     )
        #     # print(observation)
        #     return observation, 0
        # else:
        #     output = f"no such action : {action_name}"
        #     # print(output)
        #     return output, 0


@agent_registry.register("solver") # solver is also tool agent by default
class SolverAgent(BaseAgent):
    class Config:
        arbitrary_types_allowed = True

    diag_id: str = ""
    enable_prometheus: bool = True
    tools: APICaller = Field(default_factory=APICaller)
    tool_memory: BaseMemory = Field(default_factory=ChatHistoryMemory)
    tool_matcher: api_matcher = Field(default_factory=api_matcher)
    verbose: bool = Field(default=False)
    name: str = Field(default="CpuExpert")
    max_history: int = 3
    start_time: str = ""
    end_time: str = ""
    alert_str: str = ""
    alert_dict: List[dict] = []
    messages: List[dict] = []

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
        tasksolving_env = wrap_tasksolving_env(task_description, self.tools, self.tool_memory)
        
        chain = UCT_vote_function(diag_id=self.diag_id, enable_prometheus=self.enable_prometheus, start_time=self.start_time, end_time=self.end_time, agent_name=self.name, role_description=self.role_description, prompt_template=self.prompt_template, llm=self.llm,env=tasksolving_env, output_parser=self.output_parser, alert_dict=self.alert_dict, alert_str=self.alert_str, agent=self)

        print(colored(f"\n{self.name} Diagnosis!","red"))

        result_node, top_abnormal_metric_values  = chain.start(simulation_count=1,epsilon_new_node=0.3,choice_count=1,vote_candidates=2,vote_count=1,single_chain_max_step=24)

        if result_node is None:
            return {}

        prompt = "Analyze the diagnosed root causes based on above discussions in details. Note the analysis should be only about root causes in markdown format!!! And do not mention anything about the solutions!!!"
        diag_message = self.llm._construct_messages(prompt)
        diag_messages = [result_node.messages[-1]] + diag_message
        self.llm.change_messages("You are a database expert", diag_messages)
        root_causes = self.llm.parse()        
        if isinstance(root_causes, dict):
            root_causes = root_causes["content"]
        else:
            root_causes = root_causes.content
        
        # print(colored(f"\nDetected Root Causes: {root_causes}","blue"))

        prompt = "Give the solutions only based on above messages in details. Note do not mention anything about **root causes**!!! The solutions (not root causes) should be in markdown format. If there are no solutions in above messages, please answer 'No solution available'"
        solution_message = self.llm._construct_messages(prompt)
        solution_messages = [result_node.messages[-1]] + solution_message
        self.llm.change_messages("You are a database expert", solution_messages)
        solutions = self.llm.parse()
        if isinstance(solutions, dict):
            solutions = solutions["content"]
        else:
            solutions = solutions.content
        
        # print(colored(f"\nRecommended Solutions: {solutions}","white"))

        # thought = ""
        # solutions = ""
        # for message in result_node.messages:
        #     if 'content' in message and '"start_time":"xxxx"' not in message['content'].lower() and '"solution"' in message['content'].lower():

        #         contents = message['content'].split('\n')
        #         for content in contents:
        #             if "thought" in content.lower():
        #                 thought = content.strip()
        #                 thought = re.sub(r'(?i)thought:\s?', '', thought)
        #             if "solution" in content.lower():
        #                 pattern = r'(?i)"solution":\s?(.*?),\s?"'
        #                 match = re.search(pattern, content)
        #                 if match:
        #                     solutions = match.group(1)

        return {
            "root cause": root_causes,
            "diagnosis process": result_node.messages,
            "solutions": solutions,
            "topMetrics": top_abnormal_metric_values,
            "sender": self.name,
            "receiver": self.get_receiver()}
    
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

    async def astep(self):
        pass

    async def review_step(self) -> CriticMessage:
        """Asynchronous version of step"""
        prompt = "Please review the above diagnosis results, and give necessary advice to correct the unclear diagnosis and proposed solutions. Note the review should be in markdown format"
        
        prompt_message = {"role": "user", "content": prompt, "time": time.strftime("%H:%M:%S", time.localtime())}

        self.messages.append(prompt_message)

        self.llm.change_messages(self.role_description, self.messages)
        review_message = self.llm.parse()

        return review_message

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
        
        self.tool_matcher.add_tool(self.tools)

        relevant_tools = self.tool_matcher.query(Template(self.prompt_template).safe_substitute({"chat_history": self.memory.to_string(add_sender_prefix=True)}))

        tools = "\n".join([f"> {tool}: {relevant_tools[tool]}" for tool in relevant_tools])

        tools = tools.replace("{{", "{").replace("}}", "}")

        tool_names = ", ".join([tool for tool in relevant_tools])
                
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

        return Template(self.prompt_template).safe_substitute(input_arguments)

    def add_message_to_memory(self, messages: List[Message]) -> None:
        self.memory.add_message(messages)

    def reset(self) -> None:
        """Reset the agent"""
        self.memory.reset()
        # TODO: reset receiver