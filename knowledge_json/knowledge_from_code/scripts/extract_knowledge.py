import re
from llms import CustomLLM
import json

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
    except json.JSONDecodeError:
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


def describe_functions(file_content):
    functions = get_function_description(file_content)

    for i, f in enumerate(functions):
        function_name = extract_function_name(f)

        '''
        prompt = """Translate the following code lines like a diagnosis expert:
                    {}
        
                    Note.
                      1. The translation should be within one paragraph. 
                      2. Do not involve words like "pice of code" and "code" in the translation!! Speak like an expert.
                      3. Replace "returns False" with "not a root cause"; Replce "returns True" with "is a root cause".
                      4. Do not mention the function name in the translation.
                      5. The translation should be like an answer of a diagnosis expert.
                      6. Replace "a certain threshold" or "threshold" with the exact variable name like "tuple_number_threshold".
        """.format(f)
        '''
        prompt = """List all the system metrics that are used in the following code lines:
                {}
        
                Note. Only the metric names are required. Do not describe these metrics!!
        """.format(f)

        prompt_response = openai.ChatCompletion.create(
            engine="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": str(prompt)}
                ]
        )
        output_analysis = prompt_response['choices'][0]['message']['content']

        # llm = CustomLLM()
        # output_analysis = llm(prompt)


        print(f)
        print("===========================================")
        print(output_analysis)
        # write_to_json(function_name, output_analysis)
        add_to_json(function_name, output_analysis)


# input the content of python file
with open('diagnosis_code.txt', 'r') as f:
    file_content = f.read()

describe_functions(file_content)
