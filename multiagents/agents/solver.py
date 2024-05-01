from __future__ import annotations

import time
import json
from string import Template
from pydantic import Field
from typing import List
import numpy as np

from multiagents.message import SolverMessage, Message, CriticMessage
from multiagents.memory import BaseMemory, ChatHistoryMemory
from multiagents.agents import agent_registry
from multiagents.agents.base import BaseAgent
from multiagents.tools.api_retrieval import APICaller
from multiagents.reasoning_algorithms import UCT_vote_function, node_to_chain
from multiagents.reasoning_algorithms import base_env
from multiagents.tools.retriever import api_matcher
from multiagents.utils.interact import add_display_message, finish_expert_diagnosis
from multiagents.llms.sentence_embedding import sentence_embedding
from multiagents.prompt_templates.roundtable_prompts import ROUND_TABLE_PROMPT, ROUND_TABLE_PROMPT_zh

def cosine_similarity(v1, v2):
    # Normalize the vectors to unit vectors
    v1_norm = v1 / np.linalg.norm(v1)
    v2_norm = v2 / np.linalg.norm(v2)
    
    # Compute the cosine similarity by taking the dot product
    return np.dot(v1_norm, v2_norm)



class ToolNotExistError(BaseException):

    """Exception raised when parsing output from a command fails."""

    def __init__(self, tool_name=""):
        self.tool_name = tool_name

    def __str__(self):
        return f"Tool {self.tool_name} does not exist."


class wrap_tasksolving_env(base_env):
    def __init__(self, task_description, tools, tool_memory):
        super(wrap_tasksolving_env, self).__init__()

        self.task_description = task_description
        self.tool = tools
        self.tool_memory = tool_memory

        # self.input_description = "The followings are the names of the valid actions:\n"
        self.tool_names = []

        for api in self.tool.functions:
            # self.input_description += api + "\n"
            self.tool_names.append(api)
        self.tool_names.append("finish")

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
        observation = self.tool.call_function(
            parsed_response.tool, **parameters)

        return observation, 0


@agent_registry.register("solver")  # solver is also tool agent by default
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
        self, former_solution: str, advice: str, task_description: str, args
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
        tasksolving_env = wrap_tasksolving_env(
            task_description, self.tools, self.tool_memory)
        
        # Step2: compute the embedding of the alert string
        alert_embedding = sentence_embedding(self.alert_str)

        top_functions = {}
        for tool_name in self.tools.functions:
            simialrity = cosine_similarity(self.tools.functions[tool_name]["embedding"], alert_embedding)
            top_functions[tool_name] = simialrity

        if len(top_functions) > args.max_api_num:
            top_functions = dict(sorted(top_functions.items(), key=lambda item: item[1], reverse=True)[:2])
        self.tools.top_functions = {}
        for tool_name in top_functions:
            self.tools.top_functions[tool_name] = self.tools.functions[tool_name]
        self.tools.functions = self.tools.top_functions

        # Step3: run the UCT algorithm to get the diagnosis results
        chain = UCT_vote_function(
            diag_id=self.diag_id,
            enable_prometheus=self.enable_prometheus,
            start_time=self.start_time,
            end_time=self.end_time,
            agent_name=self.name,
            role_description=self.role_description,
            prompt_template=self.prompt_template,
            llm=self.llm,
            env=tasksolving_env,
            output_parser=self.output_parser,
            alert_dict=self.alert_dict,
            alert_str=self.alert_str,
            agent=self,
            language=self.language
        )

        print(f"\n[{self.name}] 开始诊断!")

        result_node, top_abnormal_metric_values = chain.start(
            simulation_count=2, epsilon_new_node=0.3, choice_count=1, vote_candidates=2, vote_count=1, single_chain_max_step=24)
        
        self.knowledge_list = []
        cur_node = result_node
        while cur_node is not None:
            for knowledge in cur_node.knowledge_list:
                if knowledge not in self.knowledge_list:
                    self.knowledge_list.append(knowledge)
            cur_node = cur_node.father

        if result_node is None:
            return {}
        if self.language == 'zh':
            prompt = "基于上述内容，详细分析诊断的根因。请注意，分析应仅针对根因，不要提及任何解决方案。以markdown格式返回。"
        else:
            prompt = "Analyze the diagnosed root causes based on above discussions in details. Note the analysis should be only about root causes in markdown format!!! And do not mention anything about the solutions!!!"
        diag_message = self.llm._construct_messages(prompt)
        diag_messages = [result_node.messages[-1]] + diag_message
        if self.language == 'zh':
            self.llm.change_messages("你是一个数据库专家。", diag_messages)
        else:
            self.llm.change_messages("You are a database expert", diag_messages)
        if self.enable_feedback():
            add_display_message('expertDiagnosis', self.name, result_node.messages[-1]['content'] + '\n\n' + prompt, diag_message[0]['time'], flag=False)
        root_causes = self.llm.parse(role=self.name, task='expert_root_cause')
        if isinstance(root_causes, dict):
            root_causes = root_causes["content"]
        else:
            root_causes = root_causes.content

        # print(colored(f"\nDetected Root Causes: {root_causes}","blue"))
        if self.language == 'zh':
            prompt = "基于上述内容，详细给出解决方案。请注意，只给出解决方案，不要提及任何根因。以markdown格式返回。如果上述消息无解决方案，请回答\"无可靠解决方案\"。"
        else:
            prompt = "Give the solutions only based on above messages in details. Note do not mention anything about **root causes**!!! The solutions (not root causes) should be in markdown format. If there are no solutions in above messages, please answer 'No solution available'"
        solution_message = self.llm._construct_messages(prompt)
        solution_messages = [result_node.messages[-1]] + solution_message
        if self.language == 'zh':
            self.llm.change_messages("你是一个数据库专家。", solution_messages)
        else:
            self.llm.change_messages("You are a database expert", solution_messages)
        if self.enable_feedback():
            add_display_message('expertDiagnosis', self.name, result_node.messages[-1]['content'] + '\n\n' + prompt, solution_message[0]['time'], flag=False)
        solutions = self.llm.parse(role=self.name, task='expert_solution')
        if isinstance(solutions, dict):
            solutions = solutions["content"]
        else:
            solutions = solutions.content
        finish_expert_diagnosis(self.name)
        # print(colored(f"\nRecommended Solutions: {solutions}","white"))

        # thought = ""
        # solutions = ""
        # for message in result_node.messages:
        # if 'content' in message and '"start_time":"xxxx"' not in
        # message['content'].lower() and '"solution"' in
        # message['content'].lower():

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
        if self.language == 'zh':
            prompt = ROUND_TABLE_PROMPT_zh
        else:
            prompt = ROUND_TABLE_PROMPT

        prompt_message = {
            "role": "user",
            "content": prompt,
            "time": time.strftime(
                "%H:%M:%S",
                time.localtime())}

        self.messages.append(prompt_message)

        self.llm.change_messages(self.role_description, self.messages)
        if self.enable_feedback():
            add_display_message('groupDiscussion', self.name, '\n\n'.join([m["content"] for m in self.messages]), self.messages[-1]['time'], flag=False)
        review_message = self.llm.parse(role=self.name, task='review')

        return review_message

    def _fill_prompt_template(
            self,
            env_description: str = "",
            tool_observation: List[str] = []) -> str:
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

        relevant_tools = self.tool_matcher.query(Template(self.prompt_template).safe_substitute(
            {"chat_history": self.memory.to_string(add_sender_prefix=True)}))

        # 目前openai给的函数调用方式是在发请求的时候作为入参，但是不太适合这里需要Thought的过程，且改动会较大，所以先不改了
        # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb
        # tools = [{"type": "function", "function": v} for v in relevant_tools.values()]

        # qwen_agent里给的模板
        if self.language == 'zh':
            tool_desc = '### {name}\n\n{name}: {description} 输入参数：{parameters}'
        else:
            tool_desc = '### {name}\n\n{name}: {description} Parameters：{parameters}'

        tools = "\n\n".join(
            [
                tool_desc.format(
                    name=tool_definition['name'],
                    description=tool_definition['description'],
                    parameters=json.dumps(tool_definition['parameters'], ensure_ascii=False)
                ).rstrip()
                for tool_definition in relevant_tools.values()
            ]
        )

        # tools = tools.replace("{{", "{").replace("}}", "}")

        tool_names = ", ".join([tool for tool in relevant_tools])
        tool_choice = ", ".join(
            [
                tool for tool in relevant_tools
                if tool not in ["match_diagnose_knowledge", "whether_is_abnormal_metric"]
            ]
        )

        self.role_description = Template(self.role_description).safe_substitute(
            {
                "agent_name": self.name,
                "tools": tools,
                "tool_names": tool_names,
            }
        )

        input_arguments = {
            "alert_info": self.alert_str,
            "agent_name": self.name,
            "env_description": env_description,
            "role_description": self.role_description,
            "chat_history": self.memory.to_string(add_sender_prefix=True),
            "tools": tools,
            "tool_names": tool_names,
            "tool_observation": "\n".join(tool_observation),
            "tool_choice": tool_choice
        }

        return Template(self.prompt_template).safe_substitute(input_arguments)

    def add_message_to_memory(self, messages: List[Message]) -> None:
        self.memory.add_message(messages)

    def reset(self) -> None:
        """Reset the agent"""
        self.memory.reset()
        # TODO: reset receiver
