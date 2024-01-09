
PREFIX = """Do the following tasks as best you can. You have access to the following tools:"""
FORMAT_INSTRUCTIONS = """Use the following format:

Task: the task you must handle
Thought: you should always think about what to do
Action: the action to take, should be one of {tool_names}
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer. (or) I give up and retry.
Final Answer: the final answer to the original input question. (or) I give up and try again.
Here is the task:
{task_description}
{input_description}
Begin!
{former_trice}"""



REACT_DIVERSE_PROMPT = '''There are some former choices.
**********************************
{previous_candidate}**********************************
I will make Action that is different from all of the above.
'''

FORMAT_INSTRUCTIONS_USER_FUNCTION = """
{input_description}
Begin!
"""