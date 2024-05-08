from __future__ import annotations

import re
from typing import Union
import json

# from langchain.schema import AgentAction, AgentFinish
from multiagents.utils.utils import AgentAction, AgentFinish
from multiagents.custom_parser import OutputParserError, output_parser_registry
from multiagents.custom_parser import OutputParser
from multiagents.response_formalize_scripts.combine_similar_answer import combine_similar_answers


@output_parser_registry.register("agent_conf")
class DBDiag(OutputParser):
    def parse(self, output) -> Union[AgentAction, AgentFinish]:
        # pdb.set_trace()
        # if output is str
        if isinstance(output, str):
            text = output
        else:
            try:
                text = output['content']
            except:
                raise OutputParserError("llm output is not str or dict")
        
        cleaned_output = text.strip()
        cleaned_output = re.sub(r"\n+", "\n", cleaned_output)

        matches = list(re.finditer(r'\n|\\n', cleaned_output))

        # cleaned_output = cleaned_output.split("\\n")
        # if len(cleaned_output) == 1:
        #     cleaned_output = cleaned_output[0].split("\n")
        if len(matches) > 1:
            raw_thought = cleaned_output[:matches[0].start()]
            raw_action = cleaned_output[matches[0].end():matches[1].start()]
            raw_action_input = cleaned_output[matches[1].end():]
        else:
            return None

        cleaned_output = [raw_thought, raw_action, raw_action_input]

        if not (cleaned_output[0].lower().startswith("thought") and
                cleaned_output[1].lower().startswith("action") and
                (cleaned_output[2].lower().startswith("action input"))):
            return None

        # action = cleaned_output[1][len("Action:") :].strip()
        # action_input = cleaned_output[2][len("Action Input:") :].strip()
        # Extract action after "Action:" (case-insensitive)
        action_split = re.split(r'(?i)^action:', cleaned_output[1], maxsplit=1)
        action = action_split[1].strip() if len(action_split) > 1 else ""

        # Extract action input after "Action Input:" (case-insensitive)
        action_input_split = re.split(r'(?i)^action input:', cleaned_output[2], maxsplit=1)
        action_input = action_input_split[1].strip() if len(action_input_split) > 1 else ""

        #print(colored("new action", "red"))
        #print(cleaned_output)

        if action.lower() in ["speak"]:

            action_input = re.sub(r"\n+", "\n", action_input)
            action_input = action_input.replace("\\\"", "\"")

            #action_input = action_input.split("\n")
            try:
                if action_input[0] == '(':
                    action_input = action_input[1:]
                if action_input[-1] == ')':
                    action_input = action_input[:-1]
                action_input = json.loads(action_input)
            except:
                print("Error in parsing diagnosis results from 'speak' action")
                
                return None

            action_json = {"diagnose": "", "solution": [], "knowledge": ""}
            
            for key in action_input:
                if "diagnose" in key:
                    if type(action_input[key]) == list and action_input[key] != []:
                        action_input[key] = combine_similar_answers(action_input[key], output_format='list')
                    elif type(action_input[key]) == str and action_input[key] != "":
                        action_input[key] = combine_similar_answers(action_input[key])

                    action_json["diagnose"] = action_input[key]
                elif "solution" in key: # list
                    if type(action_input[key]) == list and action_input[key] != []:
                        action_input[key] = combine_similar_answers(action_input[key], output_format='list')
                    elif type(action_input[key]) == str and action_input[key] != "":
                        action_input[key] = combine_similar_answers(action_input[key])
                    potential_solutions = action_input[key]

                    if isinstance(potential_solutions, str):
                        potential_solutions = potential_solutions.strip()
                        potential_solutions = re.sub(r"\n+", "\n", potential_solutions)
                        potential_solutions = potential_solutions.split("\n")

                    action_json["solution"] = potential_solutions
                elif "knowledge" in key:
                    if type(action_input[key]) == list and action_input[key] != []:
                        action_input[key] = combine_similar_answers(action_input[key], output_format='list')
                    elif type(action_input[key]) == str and action_input[key] != "":
                        action_input[key] = combine_similar_answers(action_input[key])

                    action_json["knowledge"] = action_input[key]

            return AgentFinish({"output": action_json}, text)
        
        elif action == "CallOn":
            return AgentFinish({"output": "[CallOn] " + action_input}, text)
        elif action == "RaiseHand":
            return AgentFinish({"output": "[RaiseHand] " + action_input}, text)
        elif action == "Listen":
            return AgentFinish({"output": ""}, text)
        else:            
            return AgentAction(action.lower(), action_input, text)

            # p action.lower()
            # 'obtain_start_and_end_time_of_anomaly'
            # p action_input
            # '{"input": "1692588540, 1692588630"}'

            # p action.lower()
            # 'whether_is_abnormal_metric'
            # p action_input
            # '{"start_time": 1692588540, "end_time": 1692588630, "metric_name": "cpu_usage"}'
            # p text
            # 'Thought: Now that I have obtained the start and end time of the anomaly, I should check whether the CPU usage is abnormal during that time period.\nAction: whether_is_abnormal_metric\nAction Input: {"start_time": 1692588540, "end_time": 1692588630, "metric_name": "cpu_usage"}'