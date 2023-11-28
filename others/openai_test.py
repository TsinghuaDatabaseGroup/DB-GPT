import os
from openai import OpenAI

def test_openai():

    client = OpenAI( api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
            )

    openai_model = "gpt-4"
    # gpt-3.5-turbo gpt-3.5-turbo-16k gpt-4 gpt-4-32k-0314

    prompt = "I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with \"Unknown\".\n\nQ: What is human life expectancy in the United States?\nA: Human life expectancy in the United States is 78 years.\n\nQ: Who was president of the United States in 1955?\nA: Dwight D. Eisenhower was president of the United States in 1955.\n\nQ: Which party did he belong to?\nA: He belonged to the Republican Party.\n\nQ: What is the square root of banana?\nA: Unknown\n\nQ: How does a telescope work?\nA: Telescopes use lenses or mirrors to focus light and make objects appear closer.\n\nQ: Where were the 1992 Olympics held?\nA: The 1992 Olympics were held in Barcelona, Spain.\n\nQ: How many squigs are in a bonk?\nA: Unknown\n\nQ: Where is the Valley of Kings?\nA:"

    prompt_response = client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": str(prompt)}
        ]
    )            
    output_analysis = prompt_response.choices[0].message.content

    return output_analysis


if __name__ == "__main__":

    response = test_openai()

    print(response)
