from __future__ import annotations

import re
from typing import Union
import json

# from langchain.schema import AgentAction, AgentFinish
from multiagents.utils.utils import AgentAction, AgentFinish
from multiagents.custom_parser import OutputParserError, output_parser_registry
from multiagents.custom_parser import OutputParser
from multiagents.response_formalize_scripts.combine_similar_answer import combine_similar_answers


@output_parser_registry.register("qwen_output_parser")
class QwenDBDiag(OutputParser):
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

        special_func_token = '\nAction:'
        special_args_token = '\nAction Input:'
        special_obs_token = '\nObservation:'
        special_answer_token = '\nFinal Answer:'
        i = text.rfind(special_func_token)
        j = text.rfind(special_args_token)
        k = text.rfind(special_obs_token)
        l = text.rfind(special_answer_token)
        if 0 <= i < j:  # If the text has `Action` and `Action input`,
            if k < j:  # but does not contain `Observation`,
                # then it is likely that `Observation` is omitted by the LLM,
                # （在inference的refine_messages里有处理，这里保险起见还是保持）
                # because the output text may have discarded the stop word.
                text = text.rstrip() + special_obs_token  # Add it back.
            k = text.rfind(special_obs_token)
            action = text[i + len(special_func_token):j].strip()
            action_input = text[j + len(special_args_token):k].strip()
            text = text[:k]  # Discard '\nObservation:'.

            return AgentAction(action.lower(), action_input, text)

        else:
            assert l > 0
            action_input = text[l + len(special_answer_token):]
            # 防止生成了final answer后还乱说其他的，可能还会有问题 TODO
            left = action_input.find("{")
            right = action_input.find("}")
            action_input = action_input[left:right+1]

            try:

                action_input = json.loads(action_input)
            except:
                print("Error in parsing diagnosis results")
                return None

            action_json = {"diagnose": "", "solution": [], "knowledge": ""}

            for key in action_input:
                if "diagnose" in key:
                    if type(action_input[key]) == list and action_input[key] != []:
                        action_input[key] = combine_similar_answers(action_input[key], output_format='list')
                    elif type(action_input[key]) == str and action_input[key] != "":
                        action_input[key] = combine_similar_answers(action_input[key])

                    action_json["diagnose"] = action_input[key]
                elif "solution" in key:  # list
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
