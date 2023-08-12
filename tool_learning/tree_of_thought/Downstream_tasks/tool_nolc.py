from bmtools.agent.singletool import load_single_tools
import json
import os
import requests
import yaml
from bmtools.agent.apitool import RequestTool
from bmtools import get_logger
from bmtools.models.customllm import CustomLLM
from langchain.schema import AgentAction, AgentFinish
from langchain.agents.agent import AgentOutputParser
import re
from pprint import pprint
import pdb

logger = get_logger(__name__)

FORMAT_INSTRUCTIONS = """Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

class MyMRKLOutputParser(AgentOutputParser):
    def parse(self, text: str):
        FINAL_ANSWER_ACTION = "Final Answer:"
        if FINAL_ANSWER_ACTION in text:
            return AgentFinish(
                {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
            )
        # \s matches against tab/newline/whitespace
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, text, re.DOTALL)
        if not match:
            return AgentFinish(
                {"output": text}, text
            )
            # raise OutputParserException(f"Could not parse LLM output: `{text}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        return AgentAction(action, action_input.strip(" ").strip('"'), text)

def import_all_apis(tool_json):
    '''import all apis that is a tool
    '''
    doc_url = tool_json['api']['url']
    response = requests.get(doc_url)

    # logger.info("Doc string URL: {}".format(doc_url))
    if doc_url.endswith('yaml') or doc_url.endswith('yml'):
        plugin = yaml.safe_load(response.text)
    else:
        plugin = json.loads(response.text)

    server_url = plugin['servers'][0]['url']
    if server_url.startswith("/"):
        server_url = "http://127.0.0.1:8079" + server_url
    # logger.info("server_url {}".format(server_url))

    # all_apis = []
    # for key in plugin['paths']:
    #     value = plugin['paths'][key]
    #     for method in value:
    #         api = RequestTool(root_url=server_url, func_url=key, method=method, request_info=value)
    #         all_apis.append(api)
    # return all_apis

    all_apis = []
    api_info = {}
    for key in plugin['paths']:
        value = plugin['paths'][key]
        for method in value:
            api = RequestTool(root_url=server_url, func_url=key, method=method, request_info=value)
            api_info[key] = value # 获取api详细信息
            # pprint(api_info)
            all_apis.append(api)
    return all_apis, api_info

def load_single_tools(tool_name, tool_url):
    
    # tool_name, tool_url = "datasette", "https://datasette.io/"
    # tool_name, tool_url = "klarna", "https://www.klarna.com/"
    # tool_name, tool_url =  'chemical-prop',  "http://127.0.0.1:8079/tools/chemical-prop/"
    # tool_name, tool_url =  'douban-film',  "http://127.0.0.1:8079/tools/douban-film/"
    # tool_name, tool_url =  'weather',  "http://127.0.0.1:8079/tools/weather/"
    # tool_name, tool_url =  'wikipedia',  "http://127.0.0.1:8079/tools/wikipedia/"
    # tool_name, tool_url =  'wolframalpha',  "http://127.0.0.1:8079/tools/wolframalpha/"
    # tool_name, tool_url =  'klarna',  "https://www.klarna.com/"


    get_url = tool_url +".well-known/ai-plugin.json"
    response = requests.get(get_url)

    if response.status_code == 200:
        tool_config_json = response.json()
    else:
        raise RuntimeError("Your URL of the tool is invalid.")

    return tool_name, tool_config_json

class STQuestionAnswerer:
    def __init__(self, openai_api_key = ""):
        if len(openai_api_key) < 3:
            openai_api_key = os.environ.get('OPENAI_API_KEY')

        self.openai_api_key = openai_api_key
        
    def run(self, name, meta_info, prompt_type="react-with-tool-description", query = None, return_intermediate_steps=True):

        self.all_tools_map = {}
        self.all_tools_map[name] = import_all_apis(meta_info)

        logger.info("Tool [{}] has the following apis: {}".format(name, self.all_tools_map[name]))

        if prompt_type == "react-with-tool-description":
            customllm = CustomLLM()
            description_for_model = meta_info['description_for_model'].strip()

            prefix = f"""Answer the following questions as best you can. General instructions are: {description_for_model}. Specifically, you have access to the following APIs:"""
            suffix = """Begin! Remember: (1) Follow the format, i.e,\nThought:\nAction:\nAction Input:\nObservation:\nFinal Answer:\n. The action you generate must be exact one of the given API names instead of a sentence or any other redundant text. The action input is one json format dict without any redundant text or bracket descriptions . (2) Provide as much as useful information (such as useful values/file paths in your observation) in your Final Answer. Do not describe the process you achieve the goal, but only provide the detailed answer or response to the task goal. (3) Do not make up anything. DO NOT generate observation content by yourself. (4) Read the observation carefully, and pay attention to the messages even if an error occurs. (5) Once you have enough information, please immediately use \nThought: I have got enough information\nFinal Answer: \n\nTask: {input}\n{agent_scratchpad}"""
            

            tools = self.all_tools_map[name]
            tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools]).replace("{{", "{").replace("}}", "}")

            format_instructions = FORMAT_INSTRUCTIONS.format(tool_names=", ".join([tool.name for tool in tools]))

            prompt = "\n\n".join([prefix, tool_strings, format_instructions, suffix])

            logger.info("Full prompt template: {}".format(prompt))

            name_to_tool_map = {tool.name: tool for tool in self.all_tools_map[name]}
            intermediate_steps = []
            iterations = 0
            max_iterations = 1000
            output_parser = MyMRKLOutputParser()
            while iterations <= max_iterations:
                agent_scratchpad = ""
                for action, observation in intermediate_steps:
                    agent_scratchpad += action
                    agent_scratchpad += f"\nObservation: {observation}\nThought:"
                input_at_this_round = prompt.replace("{input}", query).replace("{agent_scratchpad}", agent_scratchpad)

                print(input_at_this_round)

                full_output = customllm(prompt = input_at_this_round, stop = ['\nObservation:', '\n\tObservation:'])

                parsed_output = output_parser.parse(full_output)._asdict()
                print(parsed_output)
                # _take_next_step
                if "tool" in parsed_output:
                    tool = name_to_tool_map[parsed_output["tool"]]
                    return_direct = tool.return_direct
                    # We then call the tool on the tool input to get an observation
                    observation = tool.run(
                        parsed_output["tool_input"],
                    )
                    next_step_output = (parsed_output["tool"], observation)
                # TODO: next_step_output can contain multiple items?

                if "Final Answer" in parsed_output["log"]:
                    break

                intermediate_steps.append(next_step_output)

                # See if tool should return directly
                # tool_return = self._get_tool_return(next_step_action)
                # if tool_return is not None:
                #     return self._return(tool_return, intermediate_steps)
                iterations += 1

            exit()
        else:
            raise NotImplementedError("Other prompt types are not implemented yet.")

if __name__ == "__main__":
    # tool_name, tool_url = 'meta_analysis',  "http://127.0.0.1:8079/tools/meta_analysis/"
    tool_name, tool_url = 'wolframalpha',  "http://127.0.0.1:8079/tools/wolframalpha/"
    tool_name, tool_config = load_single_tools(tool_name, tool_url)
    print(tool_name, tool_config)
    import pdb
    pdb.set_trace()
    stqa =  STQuestionAnswerer()

    agent = stqa.run(tool_name, tool_config, prompt_type="react-with-tool-description", query="write a weather report for SF today.")