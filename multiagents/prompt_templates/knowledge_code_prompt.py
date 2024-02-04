
EXTRACT_FUNCTION_PROMPT = """Translate the following code lines like a diagnosis expert:
                    {function_content}

====================================
                    
    Note.
        1. The translation should be within one paragraph. 
        2. Do not involve words like "piece of code" and "code" in the translation!! Speak like an expert.
        3. Replace "returns False" with "not a root cause"; Replace "returns True" with "is a root cause".
        4. Do not mention the function name in the translation.
        5. The translation should be like an answer of a diagnosis expert.
        6. Replace "a certain threshold" or "threshold" with the exact variable name like "tuple_number_threshold".
"""


EXTRACT_METRIC_PROMPT = """List all the system metrics that are used in the following code lines:
                {description_content}

====================================                

    Note. Only the metric names are required. Do not describe these metrics!!
"""