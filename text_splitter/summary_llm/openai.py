import os
import time
from openai import OpenAI
from text_splitter.summary_llm.diagnosis_summary_prompts import DIAGNOSIS_SUMMARYY_PROMPT

def prompt_generation(chunk, chunk_size):
    prompt = DIAGNOSIS_SUMMARYY_PROMPT.replace("{document text}", chunk)
    prompt = prompt.replace("{max words}", str(chunk_size))
    return prompt


class OpenAISummary():
    conversation_history: dict = []
    TRY_TIME: int = 1000

    def __init__(self, max_retry: int = 100, **kwargs):
        
        self.conversation_history = []
        self.TRY_TIME = 1000

    def _construct_system_messages(self):
        return [{"role": "system", "content": "You are a document text summarizer. Please summarize the following text without lossing details and within the length limit."}]

    def _construct_messages(self, prompt: str):
        return [{"role": "user", "content": prompt}]

    def generate_response(self, prompt: str):

        role_message = self._construct_system_messages()
        messages = self._construct_messages(prompt)
        messages = role_message + messages

        client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        
        for i in range(self.TRY_TIME):
            try:
                response = client.chat.completions.create(
                    messages=messages, model="gpt-4-0613"
                )
            except Exception as e:
                print(e)
                print(f"Generate_response Exception. Try again.")
                time.sleep(.5)
                continue

            return response.choices[0].message.content