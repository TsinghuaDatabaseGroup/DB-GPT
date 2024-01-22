LOGICAL_VERIFICATION_PROMPT = f"""Now given a new knowledge:\n{{new_knowledge}}\n 
Determine whether it contains similar knowledge with an existng knowledge:\n{{exist_knowledge}}\n\n 
Please output your judgement in the following format: Output "Answer:" followed by a single answer "yes" or "no"."""

DIAG_PROMPT = """Here are some diagnosis knowledge blocks following the following dict format:
```
{
  "name": "许多死元组",
  "content": "如果访问的表中有太多的死元组，可能会导致表膨胀并降低性能。",
  "metrics": ["活元组", "死元组", "表大小", "死亡率"],
  "steps": "对于每个访问的表，如果活元组和死元组的总数在可接受的限制范围内（1000），并且表大小不太大（50MB），则不是根本原因。否则，如果死亡率也超过了阈值（0.02），则被视为根本原因。我们建议及时清理死元组。"
}
```
Note elements in "metrics" should be concrete names like "活元组", "死元组", "表大小", "死亡率", etc. rather than "metric1", "metric2", etc. "content" should be a detailed description string. "steps" should be a string that contains steps to follow to diagnose the problem.
"""

LOOKUP_FUNCTION = {
    'name': "look_up",
    'description': "Given the index of a chapter or section, return the detailed content in that chapter or section. The chapter or section may contain sub-chapters or sub-sections, keep calling the look up function on these sub-chapters or sub-sections to get more information.",
    'parameters': {
        'type': "object",
        'properties': {
            'index': {
                'type': "string",
                'description': "The chapter or section index. e.g., `1.1` or `1.4`.",
            },
        },
        'required': ["index"],
    }
}
LOOKUP_PROMPT = f"Remember: This is an interactive task. At any time, use `look_up()` to obtain the detailed content in a given chapter. The available chapters include ${{relevant_chapters}}\n"

SUBMIT_RULE_FUNCTION = {
    'name': "submit_rule",
    'description': "Submit a or multiple diagnosis knowledge blocks summarized based on the knowledge learned from the document. The diagnosis knowledge blocks should follow the dict format and all the values in the dict should be chinese.",
    'parameters': {
        'type': "object",
        'properties': {
            'blocks': {
                'type': "string",
                'description': "A list of diagnosis knowledge blocks separated by empty lines in dict format.",
            },
        },
        'required': ["knowledges"],
    }
}
SUBMIT_RULE_PROMPT = f"Use `submit_rule()` to submit knowledges.\n"

DOCUMENT_TOPIC = "query optimization"
DOCUMENT_PROMPT = "Notice that the document may not be about database diagnosis, but rather contain examples that could demonstrate how to conduct database diagnosis. Pay special attention to examples in the document."
SUMMARIZE_PROMPT_MSG = [{'role': "system", 'content': (
    f"Please summarize the document you are provided with in a few sentences. Please be brief.\n"
    f"Your summarization is later used as an index for others to quickly locate technical details about {DOCUMENT_TOPIC}.\n{DOCUMENT_PROMPT}\n"
)}]

TASK_PROMPT = "write an aspect of detailed diagnosis knowledge (e.g., only about high IO, only about slow queries) that can be learned from the document"
RULES_EXTRACTION_PROMPT_MSG = [{'role': "system", 'content': (
    f"Given a document index, please {TASK_PROMPT}.\nTry to submit knowledge blocks in the currently reading chapter one by one in order. Each knowledge block should strictly follow the dict format (with double quotes)\n"
    f"{'Extracted knowledge blocks should follow the following format.' + ' ' + DIAG_PROMPT}\n"
    f"Do not repeatedly extract the following knowledge blocks:\n${{existing_rules}}\n"
    f"Do not repeatedly lookup the following sub-chapters:\n${{used_chapters}}\n"
)}]
INDEX_TEMPLATE = "{idx} - {title}"
CONTENT_TEMPLATE = "{idx} - {title}\n{content}"
DOCUMENT_VIEW_TEMPALTE = "{summaries}\n\nDocument Index:\n{index}"


def MSG(content, role='user'):
    return [{'role': role, 'content': content}]