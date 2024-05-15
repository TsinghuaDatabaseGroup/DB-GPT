from typing import Dict, List, Union
from enum import Enum
import json
import re
from dateutil import parser, tz
from datetime import datetime, timedelta
import time
import copy
from termcolor import colored
from tqdm import tqdm
from multiagents.utils.utils import AGENT_TYPES
from multiagents.utils.markdown_format import generate_quote_content
from multiagents.agents.conversation_agent import BaseAgent
from multiagents.message import Message, SolverMessage
from multiagents.tools.metrics import current_diag_time
from multiagents.prompt_templates.diagnosis_summary_prompts import (
    DIAGNOSIS_SUMMARY_PROMPT, DIAGNOSIS_SUMMARY_PROMPT_zh
)
from multiagents.environments.decision_maker import (
    BaseDecisionMaker,
    decision_maker_registry,
)
from multiagents.environments.role_assigner import (
    BaseRoleAssigner,
    role_assigner_registry,
)

from . import env_registry as EnvironmentRegistry
from pydantic import BaseModel
from multiagents.utils.interact import set_cur_task, init_messages, add_report, add_experts


def generate_tools_content(
        command_name,
        arguments,
        execution_results,
        command_status):

    div_str = f'<details open><summary><span style="font-size: 14px; font-weight: bold; color: #333333">using Tools:</span></summary><div style="display: flex; flex-direction: column; line-height: 36px"><div style="display: flex; flex-direction: row; align-content: center"><div style="font-size: 14px; color: #333333; width: 160px; flex-shrink: 0">Command Name:</div><div style="font-size: 14px; color: #676c90!important;">{command_name}</div></div><div style="display: flex; flex-direction: row; align-content: center"><div style="font-size: 14px; color: #333333; width: 160px; flex-shrink: 0">Arguments:</div><div style="font-size: 14px; color: #676c90!important; white-space: pre-wrap">{json.dumps(arguments, indent=4)}</div></div><div style="display: flex; flex-direction: row; align-content: center"><div style="font-size: 14px; color: #333333; width: 160px; flex-shrink: 0">Command Status:</div><div style="font-size: 14px; color: #676c90!important;">{command_status}</div></div></div></details>'

    return div_str


def extract_alert_info(alert_info):

    if isinstance(alert_info, str):

        alert_info = alert_info.replace("\'", '\"')
        alert_dict = alert_info.replace("'", '"')

        alert_dict = re.sub(r'"groupKey": ".*?",', '', alert_dict)
        alert_dict = json.loads(alert_dict)
    else:
        alert_dict = alert_info

    alert_status = alert_dict['status']
    alert_status = alert_status.strip()

    # identify the first alert
    alert_desc = alert_dict['alerts'][0]['annotations']['description']
    alert_desc = alert_desc.strip()

    alert_exporter = alert_dict['alerts'][0]['labels']['instance']
    alert_exporter = alert_exporter.strip()

    # Critical High Warning Info
    alert_level = alert_dict['alerts'][0]['labels']['severity']
    alert_level = alert_level.strip()

    alert_name = alert_dict['alerts'][0]['labels']['alertname']

    starts_at = parser.parse(alert_dict['alerts'][0]['startsAt'])
    ends_at = parser.parse(alert_dict['alerts'][0]['endsAt'])

    if ends_at.year == 1:
        ends_at = starts_at + timedelta(minutes=2)

    # Convert the start and end times to seconds since the Unix epoch
    epoch = datetime(1970, 1, 1, tzinfo=tz.tzutc())  # set timezone to UTC
    starts_at_seconds = (starts_at - epoch).total_seconds()
    ends_at_seconds = (ends_at - epoch).total_seconds()

    start_date = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(starts_at_seconds))
    end_date = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(ends_at_seconds))

    starts_at_seconds = str(int(starts_at_seconds))
    ends_at_seconds = str(int(ends_at_seconds))

    alert_info = f"Alert Starts At: {start_date}\nAlert Ends At: {end_date}\nAlert Status: {alert_status}\nAlert Description: {alert_desc}\nAlert Level: {alert_level}"

    alert_dict = {"alert_name": alert_name,
                  "alert_status": alert_status,
                  "alert_level": alert_level,
                  "alert_desc": alert_desc,
                  "alert_exporter": alert_exporter,
                  "start_time": starts_at_seconds,
                  "end_time": ends_at_seconds}

    return alert_info, alert_dict


@EnvironmentRegistry.register("dba")
class DBAEnvironment(BaseModel):
    """
    A basic environment implementing the logic of conversation.

    Args:
        agents: List of agents
        rule: Rule for the environment
        max_loop_rounds: Maximum number of loop rounds number
        cnt_turn: Current round number
        last_messages: Messages from last turn
        rule_params: Variables set by the rule
    """

    role_assigner: BaseRoleAssigner
    decision_maker: BaseDecisionMaker
    agents: Dict[Enum, Union[BaseAgent, List[BaseAgent]]] = None
    reporter: BaseAgent = None
    # executor: BaseExecutor
    # evaluator: BaseEvaluator

    task_description: str
    cnt_turn: int = 0
    max_turn: int = 10
    success: bool = False

    def __init__(self, **kwargs):
        init_messages()
        
        def build_components(config: Dict, registry):
            component_type = config.pop("type")
            component = registry.build(component_type, **config)
            return component

        role_assigner = build_components(
            kwargs.pop("role_assigner", {"type": "role_description"}),
            role_assigner_registry,
        )

        decision_maker = build_components(
            kwargs.pop("decision_maker", {"type": "vertical"}),
            decision_maker_registry,
        )

        super().__init__(
            role_assigner=role_assigner,
            decision_maker=decision_maker,
            # executor=executor,
            # evaluator=evaluator,
            **kwargs,
        )

    async def step(
        self,
        args,
        advice: str = "No advice yet.",
        previous_plan: str = "No solution yet."
    ) -> List[Message]:

        print(
            '<flow>{"title": "初始化诊断报告", "content": "", "isCompleted": 0, "isRuning": 1}</flow>')
        alert_str = ""
        alert_dict = []

        for alert_info in args.alerts:
            tmp_alert_str, tmp_alert_dict = extract_alert_info(alert_info)
            alert_str = alert_str + \
                f"{len(alert_dict)+1}. " + tmp_alert_str + "\n\n"
            alert_dict.append(tmp_alert_dict)

        self.reporter.start_time = args.start_at_seconds
        self.reporter.alert_str = alert_str
        self.reporter.alert_dict = alert_dict

        # print("Report Initialization!")
        print(
            f'<flow>{{"title": "初始化诊断报告", "content": "诊断报告已经初始化", "isCompleted": 1, "isRuning": 0}}</flow>')
        # with tqdm(total=1, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
        self.reporter.initialize_report()
        #    pbar.update(1)

        # print self.reporter.report in pretty dict format
        pretty_report = json.dumps(self.reporter.report, indent=4)
        # print(pretty_report + "\n")

        # ================== vanilla model ==================
        # self.reporter.report["anomaly description"]
        # solver = self.agents[AGENT_TYPES.SOLVER][0]
        # solver.alert_str = alert_str

        # prompt = solver._fill_prompt_template("",[])
        # message = solver.llm._construct_messages(prompt)
        # system_prompt = solver.llm._construct_system_messages(solver.role_description)

        # solver.llm.change_messages(solver.role_description,system_prompt+message)
        # summarized_diags = solver.llm.parse()["content"]

        # # add label

        # root_causes = {
        #     "INSERT_LARGE_DATA": ["highly concurrent commits or highly concurrent inserts"],
        #     "LOCK_CONTENTION": ["highly concurrent updates"],
        #     "VACUUM": ["highly deletes"],
        #     "REDUNDANT_INDEX": ["too many indexes"],
        #     "MISSING_INDEXES": ["missing indexes"],
        #     "INSERT_LARGE_DATA,IO_CONTENTION": ["INSERT_LARGE_DATA","IO_CONTENTION"],
        #     "FETCH_LARGE_DATA,CORRELATED_SUBQUERY": ["FETCH_LARGE_DATA","CORRELATED SUBQUERY"],
        #     "POOR_JOIN_PERFORMANCE,CPU_CONTENTION": ["POOR JOIN PERFORMANCE","CPU CONTENTION"],
        # }

        # labels = []

        # for cause in root_causes:
        #     labels += root_causes[cause]

        # prompt = "Based on the description\n" + summarized_diags + "\n\n Output labels mentioned in the description. The available labels are  \n" + str(labels) + "===== \n Note 1. the output should be in list format. And do not output any additional information (output \"None\" if no label mentioned in the description)\n2. the output should strictly exclude lables not mentioned in the description."

        # # prompt = solver._fill_prompt_template("",[])
        # message = solver.llm._construct_messages(prompt)

        # solver.llm.change_messages(solver.role_description, message)
        # new_message = solver.llm.parse()

        # if isinstance(new_message, dict):
        #     labels = new_message["content"]
        # else:
        #     labels = new_message.content

        # return summarized_diags, labels

        # ===================================================
        set_cur_task("roleAssignment")
        print(
            '<flow>{"title": "根据异常分配诊断专家", "content": "", "isCompleted": 0, "isRuning": 1}</flow>')
        self.reporter.record["anomalyAnalysis"]["RoleAssigner"]["messages"].append(
            {"data": self.reporter.report["anomaly description"], "time": time.strftime("%H:%M:%S", time.localtime())})
        anomaly_description = self.reporter.report["anomaly description"][:100] + '...'
        anomaly_description = anomaly_description.replace(
            '\n', ' ').replace(
            '"', '\'')
        print(
            f'<flow>{{"title": "根据异常分配诊断专家", "content": "{anomaly_description}", "isCompleted": 1, "isRuning": 0}}</flow>')
        self.role_assigner.alert_str = self.reporter.report["anomaly description"]
        self.role_assigner.alert_dict = self.reporter.alert_dict

        # ================== Expert Assignment ==================
        # print(colored(f"\nRole Assignment!", "green"))

        #with tqdm(total=1, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
        selected_experts = self.role_assign(
            advice=advice, alert_info=self.role_assigner.alert_str)
        #    pbar.update(1)

        # append the names of selected_experts (e.g., selected_experts[0].name)
        # to the task description by \n
        if len(selected_experts) > args.max_hired_experts:
            selected_experts = selected_experts[:args.max_hired_experts]

        selected_expert_names = [expert.name for expert in selected_experts]
        add_experts(selected_expert_names)

        print("Assigned Experts: ", selected_expert_names)

        expert_data = []
        for expert in selected_experts:
            expert_data.append({
                "name": expert.name,
                "role": "",
                "messages": []
            })

        print(f'<flow>{{"title": "专家诊断", "content": "", "expertData": {json.dumps(expert_data)}, "isCompleted": 0, "isRuning": 1}}</flow>')
        if self.reporter.language == "zh":
            expert_select_desc = "基于上述任务描述，我决定选择下列专家来诊断：\n"
        else:
            expert_select_desc = "Based on the task description, I decide to select the following experts to diagnose the problem:\n"
        expert_select_desc += "\n".join([expert.name for expert in selected_experts])

        self.reporter.record["anomalyAnalysis"]["RoleAssigner"]["messages"].append(
            {"data": expert_select_desc, "time": time.strftime("%H:%M:%S", time.localtime())})

        # assign setting info to each agent (check)
        for agent in selected_experts:
            agent.start_time = args.start_at_seconds
            agent.end_time = args.end_at_seconds
            agent.alert_dict = alert_dict
            agent.alert_str = alert_str
            agent.diag_id = args.diag_id
            agent.enable_prometheus = args.enable_prometheus
        
        # ================== Expert Diagnosis ==================
        # count on these experts to diagnose for the alert        
        report = await self.decision_making(selected_experts, None, previous_plan, args, advice) # plans: the list of diagnosis messages

        feedbacks = []
        knowledge_list = []
        for agent in selected_experts + [self.reporter]:
            agent_knowledge_list = copy.deepcopy(agent.knowledge_list)
            for e in agent_knowledge_list:
                e["agent"] = agent.name
            agent_feedbacks = []
            if hasattr(agent.llm, "feedbacks"):
                agent_feedbacks = copy.deepcopy(agent.llm.feedbacks)
            for e in agent_feedbacks:
                e["agent"] = agent.name
            feedbacks.extend(agent_feedbacks)
            knowledge_list.extend(agent_knowledge_list)

        print(colored(f"Report Generation!","blue"))
        set_cur_task("reportDemonstration")

        root_cause_cite, solutions_cite, citations_markdown = self.cite_report(self.reporter.report['root cause'], self.reporter.report['solutions'], knowledge_list, feedbacks)

        self.reporter.report['root cause'] = root_cause_cite
        self.reporter.report['solutions'] = solutions_cite
        self.reporter.report['citations'] = citations_markdown
        
        with tqdm(total=1, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:

            # add "anomaly date", "anomaly description", "root cause", "solutions" of self.reporter in a markdown table format into the string report_markdown
            report_markdown = f"# {self.reporter.report['title']}\n\n"
            # do not add any space in front of the first '|' of each row!!
            self.reporter.report['anomaly date'] = self.reporter.report['anomaly date'].replace('\n', '<br>')
            self.reporter.report['anomaly description'] = self.reporter.report['anomaly description'].replace('\n', '<br>')
            self.reporter.report['root cause'] = self.reporter.report['root cause'].replace('\n', '<br>')
            self.reporter.report['root cause'] = self.reporter.report['root cause'].replace('# ', '')
            self.reporter.report['root cause'] = self.reporter.report['root cause'].replace('#', '')
            
            self.reporter.report['solutions'] = self.reporter.report['solutions'].replace('\n', '<br>')
            self.reporter.report['solutions'] = self.reporter.report['solutions'].replace('# ', '')
            self.reporter.report['solutions'] = self.reporter.report['solutions'].replace('#', '')

            report_markdown = report_markdown + \
                f"""|                     |       |
|---------------------|-------|
| Anomaly Date        | {self.reporter.report['anomaly date']}  |
| Anomaly Description | {self.reporter.report['anomaly description']}  |
| Root Cause          | {self.reporter.report['root cause']}  |
| Solutions           | {self.reporter.report['solutions']}  |\n\n"""
            report_markdown = report_markdown + f"## Citations\n" + self.reporter.report['citations'].strip() + '\n\n'
            report_markdown = report_markdown + f"## Diagnosis Process\n" + \
                self.reporter.report['diagnosis process'].strip()
            self.reporter.record["report"] = report_markdown
            add_report(report_markdown)

            pbar.update(1)

        for expert in expert_data:
            # find the matched key in the record
            matched_key = next((k for k in self.reporter.record['anomalyAnalysis'].keys(
            ) if k.lower() == expert['name'].lower()), '')
            if matched_key:
                expert["messages"] = self.reporter.record['anomalyAnalysis'][matched_key]["messages"]

        print(
            f'<flow>{{"title": "根据异常分配诊断专家", "content": "{anomaly_description}", "messages": {json.dumps(self.reporter.record["anomalyAnalysis"]["RoleAssigner"]["messages"])}, "isCompleted": 1, "isRuning": 0}}</flow>')
        print(f'<flow>{{"title": "专家诊断", "content": "", "messages": "[]" , "expertData": {json.dumps(expert_data)}, "isCompleted": 1, "isRuning": 0}}</flow>')
        print(
            f'<flow>{{"title": "圆桌讨论", "content": "圆桌讨论结束", "messages": {json.dumps(self.reporter.record["brainstorming"]["messages"])} , "isCompleted": 1, "isRuning": 0}}</flow>')
        print(
            f'<flow>{{"title": "报告生成", "content": "报告已经生成", "messages": {self.reporter.record["report"]} , "isCompleted": 1, "isRuning": 0}}</flow>')

        return report, self.reporter.record
    
    def gen_cite_report(self, report, citations_str):
        if self.reporter.language == "zh":
            system_prompt = (
                "给你一份数据库异常诊断报告和可能的引文列表。"
                "你的任务是在报告中标记引文索引。例如，一个段落参考了引文2，就在段落后面加上[2]。"
                "对报告的每个段落，都检查所有的引文。如果这个段落确实与引文相关，就标记它的索引。"
                "请注意，有时可能没有参考的引文，或者有多个相关引文。"
                "仅输出带有引文索引的诊断报告。"
            )
            user_prompt = f'诊断报告:{report}\n\n引文列表:\n{citations_str}'
        else:
            system_prompt = 'You will be given a database anomaly diagnosis report, and a list of potential citations. Your task is to mark the citation index in the report. For instance, if a paragraph refers to the 2nd citation, you can append "[2]" to the paragraph. For each paragraph of the report, you should check the relativity of all the citations. If the paragraph actually refers to the citation, you can mark its index. Note that sometimes there may be no available citations, or more than one relative citations.\nOnly output the diagnosis report with citation indices.'
            user_prompt = f'Diagnosis Report:{report}\n\nCitations:\n{citations_str}'
        messages = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}]
        self.reporter.llm.change_messages("", messages)
        reply = self.reporter.llm.parse()
        print(messages)
        print(reply)
        return reply['content']
    
    def cite_report(self, root_cause, solutions, knowledge_list, feedbacks):
        citations = {}
        for k in knowledge_list:
            citations[k['desc']] = generate_quote_content('[{index}] ' + f'{k["source"]}.', k["desc"])

        for feedback in feedbacks:
            if feedback['auto']:
                citations[feedback["feedback"]] = generate_quote_content('[{index}] ' + f'{feedback["agent"]}.{feedback["task"]} feedback.', feedback["feedback"])
            else:
                citations[feedback["refined_response"]] = generate_quote_content('[{index}] ' + f'{feedback["agent"]}.{feedback["task"]} editted response.', feedback["refined_response"])

        citations_list = []
        for k in citations:
            citations_list.append({'index': len(citations_list) + 1, 'citation': k})
        citations_str = str(citations_list)

        root_cause_cite = self.gen_cite_report(root_cause, citations_str)
        solutions_cite = self.gen_cite_report(solutions, citations_str)

        citations_markdown = ''

        i = 1
        for c in citations_list:
            if f'[{c["index"]}]' in root_cause_cite or f'[{c["index"]}]' in solutions_cite:
                root_cause_cite = root_cause_cite.replace(f'[{c["index"]}]', f'[{i}]')
                solutions_cite = solutions_cite.replace(f'[{c["index"]}]', f'[{i}]')
                citations_markdown += citations[c["citation"]].replace('[{index}]', f'[{i}]') + '<br>'
                i += 1

        return root_cause_cite, solutions_cite, citations_markdown


    def role_assign(
            self,
            advice: str = "",
            alert_info: str = "") -> List[BaseAgent]:
        """Assign roles to agents"""

        agents = self.role_assigner.step(
            role_assigner=self.agents[AGENT_TYPES.ROLE_ASSIGNMENT][0],
            group_members=self.agents[AGENT_TYPES.SOLVER],
            advice=advice,
            alert_info=alert_info
        )

        # random a value from 0 to len(self.agents[AGENT_TYPES.SOLVER]) - 1
        # import random
        # solver_idx = random.randint(0, len(self.agents[AGENT_TYPES.SOLVER]) - 1)
        # agents= [self.agents[AGENT_TYPES.SOLVER][0]]

        return agents

    async def decision_making(
        self,
        agents: List[BaseAgent],
        manager: List[BaseAgent],
        previous_plan: str,
        args,
        advice: str = "No advice yet.",
    ) -> List[SolverMessage]:
        # TODO: plan should be string or a special type of object?

        # initial_diag: a list of diagnosis messages from selected experts
        set_cur_task("expertDiagnosis")
        initial_diags = await self.decision_maker.astep(
            agents=agents,
            task_description=self.task_description,
            previous_plan=previous_plan,
            advice=advice,
            args=args)

        expert_data = []
        for expert in agents:
            expert_data.append({
                "name": expert.name,
                "role": "",
                "messages": []
            })
        print(f'<flow>{{"title": "专家诊断", "content": "", "expertData": {json.dumps(expert_data)}, "isCompleted": 1, "isRuning": 0}}</flow>')

        print("\n============= Finish the initial diagnosis =============")

        for i, diag in enumerate(initial_diags):

            self.reporter.record["topMetrics"] = self.reporter.record["topMetrics"] + \
                diag["topMetrics"]
            # diag["root cause"] for diag in initial_diags

            # prompt = DIAGNOSIS_SUMMARYY_PROMPT
            # prompt = prompt.replace("{diagnosis_messages}", str(diag["root cause"]))
            # message = self.reporter.llm._construct_messages(prompt)
            # self.reporter.llm.change_messages(self.reporter.role_description, message)
            # summarized_diags = self.reporter.llm.parse()

            # # if summarized_diags is of dict type
            # if isinstance(summarized_diags, dict):
            #     diag_message = summarized_diags["content"]
            # else:
            #     diag_message = summarized_diags.content

            root_causes = str(diag["root cause"]).replace('\n', '<br>')

            if self.reporter.language == "zh":
                add_str = f"<br>由{diag['sender']}判断的根因是：<br>"
            else:
                add_str = f"<br>The root causes identified by {diag['sender']}:<br>"
            self.reporter.report["root cause"] = str(
                self.reporter.report["root cause"]) + add_str + root_causes + "<br>"

            # # solution = str(diag["solutions"]).replace("\"","")
            # # solution = solution.replace("\\n", "\n")
            # solution = str(diag["solutions"])

            # prompt = DIAGNOSIS_SUMMARYY_PROMPT
            # prompt = prompt.replace("{diagnosis_messages}", str(solution))
            # message = self.reporter.llm._construct_messages(prompt)
            # self.reporter.llm.change_messages(self.reporter.role_description, message)
            # summarized_solutions = self.reporter.llm.parse()

            # # if summarized_diags is of dict type
            # if isinstance(summarized_diags, dict):
            #     summarized_solutions = summarized_solutions["content"]
            # else:
            #     summarized_solutions = summarized_solutions.content

            solutions = str(diag["solutions"]).replace('\n', '<br>')

            if self.reporter.language == "zh":
                add_str = f"<br>由{diag['sender']}推荐的解决方案是：<br>"
            else:
                add_str = f"<br>The solutions recommended by {diag['sender']}:<br>"
            self.reporter.report["solutions"] = str(
                self.reporter.report["solutions"]) + add_str + solutions + "<br>"

            if self.reporter.language == "zh":
                add_str = f"<br>{i+1}. {diag['sender']}的诊断过程是：<br>"
            else:
                add_str = f"<br>{i+1}. The diagnosis process of {diag['sender']}:<br>"
            self.reporter.report["diagnosis process"] = str(
                self.reporter.report["diagnosis process"]) + add_str

            for i, m_response in enumerate(diag["diagnosis process"]):
                if m_response['role'] != "user":

                    if i > 0 and m_response["content"] == diag["diagnosis process"][i - 1]["content"]:
                        continue

                    m_message = str(m_response["content"])

                    m_message = m_message.replace('\\n', '\n')

                    # text2charts
                    pattern = r'\[chart\] \./alert_results/{}/(\w+)\.html'.format(
                        current_diag_time)
                    matches = re.findall(pattern, m_message)
                    for metric_name in matches:
                        chart_str = f'[chart] ./alert_results/{current_diag_time}/{metric_name}.html'
                        with open(f"./alert_results/{current_diag_time}/{metric_name}.html", "r") as f:
                            chart_content = f.read()

                        if chart_content != "":
                            m_message = m_message.replace(
                                chart_str, ' \n ' + chart_content + ' \n ')
                        else:
                            # remove non-existing charts
                            m_message = m_message.replace(chart_str, "")

                    pattern = r'\[chart\].*?\.html'
                    m_message = re.sub(
                        pattern, '', str(m_message), flags=re.DOTALL)

                    m_message = m_message.replace("']\"", "")
                    m_message = m_message.replace("’]", "")
                    m_message = m_message.replace("']", "")
                    m_message = m_message.strip()

                    # text2code
                    pattern = r"Action: (?P<action>[^\n]+)\nAction Input: (?P<input>\{.*?\})"

                    for match in re.finditer(
                            pattern, m_message, re.IGNORECASE | re.DOTALL):
                        action = match.group('action')
                        action_input = match.group('input')

                        # Formatting it into Markdown code format
                        # markdown_str = f"```\n{action}{action_input}\n```"

                        markdown_str = generate_tools_content(
                            action, action_input, "", "Success")
                        m_message = m_message.replace(
                            match.group(0), markdown_str)

                    m_message = m_message.replace("\n", "<br>")
                    m_message = re.sub(r'(?:<br>){2,}', '<br><br>', m_message)

                    self.reporter.report["diagnosis process"] = str(
                        self.reporter.report["diagnosis process"]) + m_message + "\n"
                    if 'time' not in m_response:
                        m_response['time'] = time.strftime(
                            "%H:%M:%S", time.localtime())

                    if diag['sender'] not in self.reporter.record["anomalyAnalysis"]:
                        self.reporter.record["anomalyAnalysis"][diag['sender']] = {
                            "messages": []}
                        self.reporter.record["anomalyAnalysis"][diag['sender']]["messages"].append(
                            {"data": m_message, "time": m_response['time']})
                    else:
                        self.reporter.record["anomalyAnalysis"][diag['sender']]["messages"].append(
                            {"data": m_message, "time": m_response['time']})

        self.reporter.messages = []
        for agent in agents:
            agent.messages = []

        for i, diag in enumerate(initial_diags):
            if self.reporter.language == 'zh':
                prompt = DIAGNOSIS_SUMMARY_PROMPT_zh
            else:
                prompt = DIAGNOSIS_SUMMARY_PROMPT

            diag_process = ""
            pre_content = ""

            for j, diag in enumerate(diag["diagnosis process"]):
                if j > 0 and diag["content"] != pre_content:
                    if "Thought:" in diag["content"]:
                        diag_process = '\n' + diag_process + \
                            diag["content"].strip() + '\n'
                    else:
                        diag_process = diag_process + \
                            diag["content"].strip() + '\n'
                    pre_content = diag["content"]

            prompt = prompt.replace("{diagnosis_messages}", diag_process)
            message = self.reporter.llm._construct_messages(prompt)
            self.reporter.llm.change_messages(
                self.reporter.role_description, message)
            summarized_diags = self.reporter.llm.parse(role=self.reporter.name, task='summary')

            # if summarized_diags is of dict type
            if isinstance(summarized_diags, dict):
                diag_message = {
                    "role": "assistant",
                    "content": summarized_diags["content"],
                    "time": time.strftime(
                        "%H:%M:%S",
                        time.localtime())}
            else:
                diag_message = {
                    "role": "assistant",
                    "content": summarized_diags.content,
                    "time": time.strftime(
                        "%H:%M:%S",
                        time.localtime())}
            #Message(content={"diagnose": summarized_diags.content}, sender="summary")

            # self.reporter.messages.append(diag_message)
            for agent in agents:
                agent.messages.append(diag_message)

        print(
            '<flow>{"title": "圆桌讨论", "content": "", "isCompleted": 0, "isRuning": 1}</flow>')
        set_cur_task("groupDiscussion")
        # print(colored(f"Cross Review!", "yellow"))

        # discuss over the summarized initial_diags results
        for agent in agents:
            # with tqdm(total=1, bar_format='{l_bar}{bar}|
            # {n_fmt}/{total_fmt}') as pbar:
            review = await agent.review_step()
            # pbar.update(1)

            if isinstance(
                    review,
                    dict) and "content" in review and review["content"] != "":
                for agent2 in agents:
                    agent2.messages.append(review)

                self.reporter.messages.append(review)

                if 'time' not in review:
                    self.reporter.record["brainstorming"]["messages"].append(
                        {
                            "sender": agent.name,
                            "data": review["content"],
                            "time": time.strftime(
                                "%H:%M:%S",
                                time.localtime())})
                else:
                    self.reporter.record["brainstorming"]["messages"].append(
                        {"sender": agent.name, "data": review["content"], "time": review['time']})
                    
                print(f"{agent.name}评审意见：", review["content"])
                # {
                #     "sender":"ChiefDBA",
                #     "data":"#diagnose /n xxxxxx /n  # solution /n XXXXXX/n   # knowledge /n  XXXXX/n  下面展示图表 ```chart xxczxczxczczxc ```` ",
                #     "time":"message sending time"
                # }
        print(
            f'<flow>{{"title": "圆桌讨论", "content": "圆桌讨论结束", "isCompleted": 1, "isRuning": 0}}</flow>')
        # review the diagnosis results by the reporter
        print(
            '<flow>{"title": "报告生成", "content": "", "isCompleted": 0, "isRuning": 1}</flow>')
        set_cur_task("reportGeneration")
        self.reporter.update_diagnosis()
        self.reporter.add_diagnosis_labels()
        self.reporter.update_solutions()
        print(
            f'<flow>{{"title": "报告生成", "content": "报告已经生成", "isCompleted": 1, "isRuning": 0}}</flow>')

        return self.reporter.report

    def is_done(self):
        """Check if the environment is done"""
        return self.cnt_turn >= self.max_turn or self.success

    def set_task_description(self, task_description: str = ""):
        self.task_description = task_description

    def reset(self) -> None:
        """Reset the environment"""
        self.cnt_turn = 0