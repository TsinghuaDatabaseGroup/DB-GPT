import os
import sys
sys.path.append('../../../')

import re
import openai
import json
from prompts.knowledge_code_prompt import EXTRACT_FUNCTION_PROMPT, EXTRACT_METRIC_PROMPT
import pdb


def add_to_json(cause_name, desc):
    # First, read the existing data
    try:
        with open('root_causes_dbmind.jsonl', 'r', encoding='utf-8') as rf:
            data = json.load(rf)
    except json.JSONDecodeError:
        data = []

    # add the new data
    success = False
    for i, d in enumerate(data):
        if d["cause_name"] == cause_name:
            data[i]["metrics"] = desc
            success = True
            break
    if success == True:
        # Write the data back to the file
        with open('root_causes_dbmind.jsonl', 'w', encoding='utf-8') as wf:
            json.dump(data, wf, indent=4)


def write_to_json(cause_name, desc):
    # First, read the existing data
    try:
        with open('root_causes_dbmind.jsonl', 'r', encoding='utf-8') as rf:
            data = json.load(rf)
    except:
        data = []

    # Append the new data
    data.append({"cause_name": cause_name, "desc": desc})

    # Write the data back to the file
    with open('root_causes_dbmind.jsonl', 'w', encoding='utf-8') as wf:
        json.dump(data, wf, indent=4)

def get_function_description(file_content):
    functions = []
    func_blocks = file_content.split('@property')
    for func in func_blocks:
        if "def" in func:
            functions.append(func)

    print(len(functions))

    return functions


def extract_function_name(string):

    lines = string.split('\n')
    for line in lines:
        if "def" in line:
            string = line
            break

    match = re.search(r'def\s+(\w+)\(', string)
    if match:
        return match.group(1)
    else:
        return None


def describe_functions(file_content, key):


    openai_model = "gpt-3.5-turbo"
    openai.api_key = os.environ["OPENAI_API_KEY"]

    functions = get_function_description(file_content)[:2]

    for i, f in enumerate(functions):
        function_name = extract_function_name(f)

        if key == "desc":
            prompt = EXTRACT_FUNCTION_PROMPT
            prompt = prompt.replace("{function_content}", f)

            prompt_response = openai.ChatCompletion.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": str(prompt)}
                ]
            )            
            output_analysis = prompt_response['choices'][0]['message']['content']
            # llm = CustomLLM()
            # output_analysis = llm(prompt)

            #pdb.set_trace()

            write_to_json(function_name, output_analysis)

        elif key == "metrics":
            prompt = EXTRACT_METRIC_PROMPT
            prompt = prompt.replace("{description_content}", f)

            prompt_response = openai.ChatCompletion.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": str(prompt)}
                ]
            )
            output_analysis = prompt_response['choices'][0]['message']['content']

            add_to_json(function_name, output_analysis)

        else:
            raise ValueError("key should be either 'desc' or 'metrics'")


if __name__ == "__main__":
    with open('diagnosis_code.txt', 'r') as f:
        file_content = f.read()

    describe_functions(file_content, "desc")

    describe_functions(file_content, "metrics")
