LOGICAL_VERIFICATION_PROMPT = f"""Now given a new knowledge:\n{{new_knowledge}}\n 
Determine whether it contains similar knowledge with an existng knowledge:\n{{exist_knowledge}}\n\n 
Please output your judgement in the following format: Output "Answer:" followed by a single answer "yes" or "no"."""

DIAG_PROMPT = """Here are some diagnosis knowledge blocks following the following dict format:
```
{"name": "many_dead_tuples",
"content": "If the accessed table has too many dead tuples, it can cause bloat-table and degrade performance",
"metrics": ["live_tuples", "dead_tuples", "table_size", "dead_rate"],
"steps": "For each accessed table, if the total number of live tuples and dead tuples is within an acceptable limit (1000), and table size is not too big (50MB), it is not a root cause. Otherwise, if the dead rate also exceeds the threshold (0.02), it is considered a root cause. And we suggest to clean up dead tuples in time."}
```"""

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
LOOKUP_PROMPT = f"Remember: This is an interactive task. At any time, use `look_up()` to obtain the detailed content in a given chapter. The available chapters include ${{alert_info}}\n"

SUBMIT_RULE_FUNCTION = {
    'name': "submit_rule",
    'description': "Submit a or multiple diagnosis knowledge blocks summarized based on the knowledge learned from the document. The diagnosis knowledge blocks should follow the dict format.",
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

TASK_PROMPT = "write database diagnosis knowledge that can be learned from the document"
RULES_EXTRACTION_PROMPT_MSG = [{'role': "system", 'content': (
    f"Given a document index, please {TASK_PROMPT}.\n{DOCUMENT_PROMPT}\nIf you are not sure, try to look up chapters and submit knowledge blocks in the currently reading chapter one by one in order. In case that you could not find any knowlege or the corresonding, please try to look up other chapters.\n"
    f"{'Extracted knowledge blocks should follow the following format.' + ' ' + DIAG_PROMPT}\n"
    f"{LOOKUP_PROMPT}\n"
    f"{SUBMIT_RULE_PROMPT}\n"
)}]
INDEX_TEMPLATE = "{idx} - {title}"
CONTENT_TEMPLATE = "{idx} - {title}\n{content}"
DOCUMENT_VIEW_TEMPALTE = "{summaries}\n\nDocument Index:\n{index}"


def MSG(content, role='user'):
    return [{'role': role, 'content': content}]