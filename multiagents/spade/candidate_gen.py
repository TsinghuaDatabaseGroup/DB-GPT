"""
We refer to https://github.com/shreyashankar/spade-experiments.
This file represents the assertion concept and candidate generator. It takes in a prompt template and outputs a set of assertion concepts to check for, based on our taxonomy of assertion concept categories. Then it synthesizes python functions.
"""
import json
import difflib

# import nltk
# nltk.download("punkt")
import nltk
nltk.data.path.append('./nltk_data')
from nltk.tokenize import sent_tokenize

from dotenv import load_dotenv

import ast
import logging
import re

from typing import List, Dict

from .assertion_gen import generate_assertions

from multiagents.llms.openai import call_openai

# from litellm import RateLimitManager

## init RateLimitManager
# handler = RateLimitManager(max_requests_per_minute=60, max_tokens_per_minute=9000)

# litellm.success_callback = ["langfuse"]
# litellm.failure_callback = ["langfuse"]

load_dotenv()

CONCEPT_TEMPLATE = """Here is the diff for my prompt template:

"{prompt_diff}"

Based on the changed lines, I want to write assertions for my LLM pipeline to run on all pipeline responses. Here are some categories of assertion concepts I want to check for:

- Presentation Format: Is there a specific format for the response, like a comma-separated list or a JSON object?
- Example Demonstration: Does theh prompt template include any examples of good responses that demonstrate any specific headers, keys, or structures?
- Workflow Description: Does the prompt template include any descriptions of the workflow that the LLM should follow, indicating possible assertion concepts?
- Count: Are there any instructions regarding the number of items of a certain type in the response, such as “at least”, “at most”, or an exact number?
- Inclusion: Are there keywords that every LLM response should include?
- Exclusion: Are there keywords that every LLM response should never mention?
- Qualitative Assessment: Are there qualitative criteria for assessing good responses, including specific requirements for length, tone, or style?
- Other: Based on the prompt template, are there any other concepts to check in assertions that are not covered by the above categories, such as correctness, completeness, or consistency?

Give me a list of concepts to check for in LLM responses. Each item in the list should contain a string description of a concept to check for, its corresponding category, and the source, or phrase in the prompt template that triggered the concept. For example, if the prompt template is "I am a still-life artist. Give me a bulleted list of colors that I can use to paint <object>.", then a concept might be "The response should include a bulleted list of colors." with category "Presentation Format" and source "Give me a bulleted list of colors".

Your answer should be a JSON list of objects within ```json ``` markers, where each object has the following fields: "concept", "category", and "source". This list should contain as many assertion concepts as you can think of, as long are specific and reasonable."""


def show_diff(template_1: str, template_2: str):
    # Split the templates into sentences
    if isinstance(template_1, list):
        template_1 = str(template_1)
    if isinstance(template_2, list):
        template_2 = str(template_2)

    sent_1 = sent_tokenize(template_1)
    sent_2 = sent_tokenize(template_2)

    diff = list(difflib.unified_diff(sent_1, sent_2))

    # Convert diff to string
    diff = "\n".join(diff)
    return diff


async def generate_concepts_and_assertions(
    prompt_template: str,
    prev_prompt_template: str,
    example_prompt: str,
    example_response: str,
) -> dict:
    """
    Generate assertion concepts to check for in the prompt template.

    Args:
    - prev_prompt_template: the previous template for the prompt
    - prompt_template: the template for the prompt

    Returns:
    - concepts: the assertion concepts to check for in the prompt template
    """
    # Get diff / new lines added
    prompt_diff = show_diff(prev_prompt_template, prompt_template)
    print(f"Prompt diff: {prompt_diff}")

    # If diff is empty, skip
    if len(prompt_diff.strip()) == 0:
        return None

    # Construct prompt to LLM
    messages = [
        {
            "content": "You are an expert Python programmer and helping me write assertions for my LLM pipeline. An LLM pipeline accepts an example and prompt template, fills the template's placeholders with the example, and generates a response.",
            "role": "system",
        },
        {
            "content": CONCEPT_TEMPLATE.format(prompt_diff=prompt_diff),
            "role": "user",
        },
    ]

    # Generate concepts
    try:
        reply = call_openai(messages)

        # Parse reply within ```json ``` markers
        reply = re.search(r"```json(.*?)\n```", reply, re.DOTALL).group(1)

        concepts = json.loads(reply)

        # Now generate assertions
        assertions = await generate_assertions(
            prompt_template, example_prompt, example_response, concepts
        )

        return {"concepts": concepts, "assertions": assertions}

    except Exception as e:
        logging.error(e)
        return None


async def generate_candidate_assertions(
    prompt_templates: List[str], responses: List[str]
) -> List[str]:
    all_assertions = []
    all_concepts = []

    # Go through each consecutive pair of prompt templates
    for prev_template, curr_template, curr_response in zip(
        prompt_templates[:-1], prompt_templates[1:], responses[1:]
    ):

        # Gen assertions
        print("Generating assertions...")
        concepts_and_assertions = await generate_concepts_and_assertions(
            curr_template, prev_template, curr_template, curr_response
        )

        if not concepts_and_assertions:
            logging.info("No concepts and assertions generated.")
            continue

        logging.info(f"Found {len(concepts_and_assertions['concepts'])} concepts.")

        all_concepts.append(concepts_and_assertions["concepts"])
        all_assertions.extend(concepts_and_assertions["assertions"])

    # Ask GPT-4 to repeat the assertions (changing repeated function names)
    all_assertions_str = "\n".join(all_assertions)

    reply = call_openai(
        messages=[
            {
                "role": "system",
                "content": "You are an expert Python programmer. You will review code and check if there are functions with the same name. If a function name is repeated, you will change it to a new name. You should also edit the code to include a variable called ALL_FUNCTIONS that contains a list of all function names. ALL_FUNCTIONS should be a list of functions, not the strings of their names. ALL_FUNCTIONS should be at the end of the code.",
            },
            {
                "role": "user",
                "content": f"Here is the code:\n\n```python\n{all_assertions_str}\n```\n\nOutput a new version of the code with all function names changed to be distinct and the ALL_FUNCTIONS variable, within ```python ``` ticks. Do not modify any of the code within the functions, and do not delete any functions.",
            },
        ],
    )

    # Extract all functions within ```python\n ``` markers
    function_code = re.findall(r"```python(.*?)```", reply, re.DOTALL)

    # Return all concepts and assertions
    return all_concepts, function_code
