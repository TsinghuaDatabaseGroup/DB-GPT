#!/usr/bin/env python
# coding=utf-8
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
import requests, json
import os

import openai

class CustomLLM(LLM):
    
    n: int = 0

    @property
    def _llm_type(self) -> str:
        return "custom"
    
    def _call(self, prompt, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Content-Type": "application/json"
        }

        # Assume this is an url providing your customized LLM service, we use the openai api as an example.
        url = "http://47.254.22.102:8989/chat"
        
        if isinstance(prompt, str):
            message = [
                {"role": "system", "content": "You are a user what to consult the assistant."},
                {"role": "user", "content": prompt},
            ]
        else:
            message = prompt

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": message,
            "max_tokens": 2048,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "temperature": 0.0,
            "best_of": 3,
            "stop": stop,
        }
        try_times = 10
        while(try_times > 0):
            try:
                response = requests.post(url, json=payload, headers=headers)
                if isinstance(prompt, str):
                    output = json.loads(response.text)["choices"][0]["message"]["content"]
                else:
                    output = response.text
                break
            except:
                try_times -= 1
                continue
        if try_times == 0:
            raise RuntimeError("Your LLM service is not available.")

        # print("\n--------------------")
        # print(prompt)
        # print("\n********************")
        # print(output)
        # print("\n--------------------")
        # input()

        return output
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"n": self.n}

    
if __name__ == "__main__":

    llm = CustomLLM()
    openai.api_key = os.environ["OPENAI_API_KEY"]
    
    with open('/Users/xuanhe/Documents/our-paper/instructdb/code/BMTools/bmtools/tools/database/data/tpch10x/extracted_sqls_s103_tpch_1gb.txt', 'r') as rf:
        with open('/Users/xuanhe/Documents/our-paper/instructdb/code/BMTools/bmtools/tools/database/data/tpch10x/extracted_texts_s103_tpch_1gb.txt', 'a') as wf:
            for i,line in enumerate(rf.readlines()):
                if i >= 71:
                    if ";" in line:
                        prompt = "Please convert the following sql query into one natural language sentence: \n" + line + "\n Note. 1) Do not mention any other information other than the natural language sentence; 2) Must use the origin table and column names in the sql query."

                        fail = 1
                        for repeat in range(3):
                            try:
                                # response = openai.Completion.create(
                                # model="text-davinci-003",
                                # prompt=prompt,
                                # temperature=0,
                                # max_tokens=1000,
                                # top_p=1.0,
                                # frequency_penalty=0.0,
                                # presence_penalty=0.0,
                                # stop=["#", ";"]
                                # )
                                text = llm(prompt)
                                fail = 0

                                wf.write(text+'\n')
                                print(text)
                                if i % 100 == 0:
                                    print("processed ", i, " queries")

                                break

                            except:
                                print("openai.error.RateLimitError")
                                continue

                        if fail == 1:
                            raise Exception("OpenAI API call failed after 3 retries")

'''
    with open('./tpch10x/text2res_single_table2.json', 'r') as json_file:
        json_data = json.load(json_file)

    new_json_data = []
    for i,item in enumerate(json_data):
        sql = item['sql']
        print("========= ", i, sql)
        prompt = "Please convert the following sql query into one natural language sentence: \n" + sql + "\n Note. 1) Do not mention any other information other than the natural language sentence; 2) Must use the origin table and column names in the sql query."
        text = llm(prompt)
        item['text'] = text
        new_json_data.append(item)
        #print(llm("Describe Shanghai in 200 words."))

    with open("text2res_single_table3.json", "w") as f:
        json.dump(new_json_data, f)
'''
