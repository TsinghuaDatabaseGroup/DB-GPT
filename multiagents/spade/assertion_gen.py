"""
We refer to https://github.com/shreyashankar/spade-experiments.
Given a prompt template and associated concepts, generate python
functions that can be used to check for those concepts in LLM responses.
"""
import json

from dotenv import load_dotenv

import ast
import logging
import re
from typing import List

# import litellm

# from litellm import RateLimitManager

## init RateLimitManager
# handler = RateLimitManager(max_requests_per_minute=60, max_tokens_per_minute=9000)

# litellm.success_callback = ["langfuse"]
# litellm.failure_callback = ["langfuse"]

from multiagents.llms.openai import call_openai

load_dotenv()

FUNCTION_GEN_TEMPLATE = """Here is my prompt template:

"{prompt_template}"

Here is an example and its corresponding LLM response:

Example formatted LLM prompt: {example_prompt}
LLM Response: {example_response}

Here are the concepts I want to check for in LLM responses:

{concepts}

Give me a list of assertions as Python functions that can be used to check for these concepts in LLM responses. Assertion functions should not be decomposed into helper functions. Assertion functions can leverage the external function `ask_llm` if the concept is too hard to evaluate with Python code alone (e.g., qualitative criteria). The `ask_llm` function accepts formatted_prompt, response, and question arguments and submits this context to an expert LLM, which returns True or False based on the context. Since `ask_llm` calls can be expensive, you can batch similar concepts that require LLMs to evaluate into a single assertion function, but do not cover more than two concepts with a function. For concepts that are ambiguous to evaluate, you should write multiple different assertion functions (e.g., different `ask_llm` prompts) for the same concept(s). Each assertion function should have no more than one `ask_llm` call.

Each function should take in 2 args: prompt (string), and LLM response (string). Each function shold return a boolean indicating whether the response satisfies the concept(s) covered by the function. Here is a sample assertion function for an LLM pipeline that generates summaries:

```python
async def assert_simple_and_coherent_narrative(prompt: str, response: str):
    # Check that the summary form a simple, coherent narrative telling a complete story.

    question = "Does the summary form a simple, coherent narrative telling a complete story?"
    return await ask_llm(prompt, response, question)
```

Your assertion functions should be distinctly and descriptively named, and they should include a short docstring describing what the function is checking for. All functions should be asynchronous and use the `await` keyword when calling `ask_llm`."""


async def generate_assertions(
    prompt_template: str, example_prompt: str, example_response: str, concepts: List
) -> List:
    """
    Generate assertion functions to check for in example-prompt-LLM-response triples.

    Args:
    - prompt_template: the template for the prompt
    - example_prompt: a formatted prompt template on some example variables
    - example_response: the response from the LLM to the example_prompt
    - concepts: the assertion concepts to check for in the prompt template

    Returns:
    - functions: the assertion functions to check for in example-prompt-LLM-response triples
    """
    # Construct prompt to LLM
    messages = [
        {
            "content": "You are an expert Python programmer and helping me write assertions for my LLM pipeline. An LLM pipeline accepts an example and prompt template, fills the template's placeholders with the example, and generates a response.",
            "role": "system",
        },
        {
            "content": FUNCTION_GEN_TEMPLATE.format(
                prompt_template=prompt_template,
                example_prompt=example_prompt,
                example_response=example_response,
                concepts=concepts,
            ),
            "role": "user",
        },
    ]

    # Generate functions
    try:
        reply = call_openai(messages=messages)

        # Extract all functions within ```python\n ``` markers
        functions = re.findall(r"```python(.*?)```", reply, re.DOTALL)
        functions = [f.strip() for f in functions]
        functions = [f for f in functions if f != ""]

        return functions
    except Exception as e:
        logging.error(e)
        return None