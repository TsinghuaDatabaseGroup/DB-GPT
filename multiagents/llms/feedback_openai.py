import time

from configs import DIAGNOSE_USER_FEEDBACK_PATH
from . import llm_registry
from .openai import OpenAIChat, call_openai
from multiagents.spade.candidate_gen import generate_candidate_assertions
import asyncio, concurrent.futures
import re
from multiagents.localized_llms.inference import classify
import copy
from .doc_kb import DocKnowledgeBase
from langchain.docstore.document import Document
from rank_bm25 import BM25Okapi
import logging
from server.utils import run_async

USERINPUTREADFROMFILE = True

FEEDBACK_ITERATIONS = 3

REFLECTION_PROMPT = 'Your previous response failed some checks, and you should improve it to pass the checks. Here are the checks you failed:\n{failed_assertions}'

EXTRACT_RULE_PROMPMT = 'I am not satisfied with your response. I shall give you a response I prefer. Please compare their differences, and summarize the differences into rules for providing better response, using the format of \"if..., then...\". Give it in sections. Each is an independent rule. Directly give the content of the rule. Do not answer anything else. Be precise and concise.\n\nBelow is my preferred response:\n{preferred_output}'

COMPARE_CONTRADICTORY_PROMPT = "\
I will give you two rules. \
Please help me classify whether the contents of these two rules are contradictory. \
You are only allowed to give me the answer, selecting from \"contradictory\" and \"not contradictory\".\n\n\
"

COMPARE_IDENTICAL_PROMPT = "\
I will give you two rules. \
Please help me classify whether the contents of these two rules are exactly identical. \
You are only allowed to give me the answer, selecting from \"identical\" and \"not identical\".\n\n\
"

def parse_assertions(assertions):
    assertions_code = {}
    assertions_rstrip = assertions[:assertions.find('ALL_FUNCTIONS = [')]
    res = re.split(r'async def (.*?)\(prompt: str, response: str\)', assertions_rstrip)
    for i in range(1, len(res) - 1, 2):
        assertions_code[res[i]] = f'async def {res[i]}(prompt: str, response: str)' + res[i + 1].rstrip()
    return assertions_code

async def ask_llm(prompt, response, question):
    # Placeholder for asking an expert a true/false question
    # In practice, this would involve a complex implementation potentially requiring human input

    messages = [
        {
            "content": f"You are an evaluator for an AI database diagnosis assistant:\n\n{prompt}\n\nHere is the response:\n{response}",
            "role": "system",
        },
        {
            "content": f"{question}\nOnly answer yes or no.",
            "role": "user",
        },
    ]

    reply = call_openai(messages)

    # get the cost
    # completion_tokens = response["usage"]["completion_tokens"]
    # prompt_tokens = response["usage"]["prompt_tokens"]

    # get the response
    # reply = response["choices"][0]["message"]["content"]

    if "yes" in reply.lower():
        # return prompt_tokens, completion_tokens, True
        return True

    # return prompt_tokens, completion_tokens, False
    return False

def parse_messages(messages, mark_idx):
    if mark_idx == 4:
        return messages[1]['content'], "Analyze the diagnosed root causes based on above discussions in details. Note the analysis should be only about root causes in markdown format!!! And do not mention anything about the solutions!!!"
        
    if mark_idx == 5:
        return messages[1]['content'], "Give the solutions only based on above messages in details. Note do not mention anything about **root causes**!!! The solutions (not root causes) should be in markdown format."
    
    if mark_idx == 6:
        pre_instruction = 'Please provide a searchable summary of the input diagnosis procedures or recommended solutions without lossing important information. The input is as follows:'

        post_instruction = '===\nNote \n1. you are an expert and do not miss any important information!!!\n2. response with a list of key points of the input diagnosis procedures or recommended solutions (e.g. \"1. ...<br>2. ...<br>3. ...\"). Do not add any additional content!!!\n3. The key points should be strictly separated by <br> (\"1. ...<br>2. ...<br>3. ...\")!!!! Do not use markdown format and # headings!!!\n4. Do not mention anything about what are the charts like!! Ignore charts!!!\n5. Do not say anything like \"As an AI\"!!'

        pre_idx = messages[1]['content'].find(pre_instruction) + len(pre_instruction)
        post_idx = messages[1]['content'].find(post_instruction)
        return messages[1]['content'][pre_idx:post_idx].strip(), pre_instruction + '\n\n' + post_instruction
    
    if mark_idx == 7:
        return '\n\n'.join([m["content"] for m in messages[1:-1]]), messages[-1]["content"]
    
    if mark_idx == 8:
        pre_instruction = 'You are writing a report. Please optimize the following solutions based on the above review advice. The solutions are:'

        post_instruction = "===\n Note 1. the output should be in markdown format.\n2. do not any additional content like 'Sure' and 'I will refine the solutions based on the above advice'. 3. Do not add anything about root causes!!!"

        pre_idx = messages[-1]['content'].find(pre_instruction) + len(pre_instruction)
        post_idx = messages[-1]['content'].find(post_instruction)
        return messages[1]['content'][pre_idx:post_idx].strip() + messages[-1]['content'][pre_idx:post_idx].strip(), pre_instruction + '\n\n' + post_instruction
    
    if mark_idx == 9:
        pre_instruction = 'You are writing a report. Please give the refined root cause analysis based on the above review advice. The root cause analysis is as follows:'

        post_instruction = "===\n Note 1. the output should be in markdown format.\n2. do not any additional content like 'Sure' and 'I will refine the anomaly diagnosis description based on the above advice. 3. Do not add anything about solutions!!!'"

        pre_idx = messages[-1]['content'].find(pre_instruction) + len(pre_instruction)
        post_idx = messages[-1]['content'].find(post_instruction)
        return messages[1]['content'][pre_idx:post_idx].strip() + messages[-1]['content'][pre_idx:post_idx].strip(), pre_instruction + '\n\n' + post_instruction
    
    if mark_idx == 11:
        post_instruction = "Now you need to select experts with diverse identity to correctly analyze the root causes of the given alert. The names of available experts are:\n['CpuExpert', 'MemoryExpert', 'IoExpert', 'WorkloadExpert', 'QueryExpert', 'WriteExpert', 'IndexExpert', 'ConfigurationExpert']\n\nWhich experts will you recruit to generate an accurate solution? Note you can only select one to three experts!!!\n\n# Response Format Guidance\nYou should respond with a list of expert names. For example:\n1. CpuExpert\n2. QueryExpert\n...\n\nOnly respond with the names of selected experts (separated by spaces). Do not include your reason."

        post_idx = messages[-1]['content'].find(post_instruction)
        return messages[-1]['content'][:post_idx].strip(), post_instruction

    return  None, None

def compare_rules(rule1, rule2, compare_prompt):

    prompt = compare_prompt + '1. ' + rule1 + '\n2. ' + rule2 + '\nAnswer: '
    return prompt

pool = concurrent.futures.ThreadPoolExecutor()

@llm_registry.register("feedback-gpt-4")
@llm_registry.register("feedback-gpt-3.5-turbo")
class FeedbackOpenAIChat(OpenAIChat):
    kb: DocKnowledgeBase = None
    def __init__(self, max_retry: int = 100, **kwargs):
        super().__init__(max_retry=max_retry, **kwargs)
        self.kb = DocKnowledgeBase()

    async def feedback(self, messages, instruction, output, feedback):
        instruction_feedback = f'{instruction}\n\n{feedback}'

        messages.append({"role": "assistant", "content": output})
        messages.append({"role": "user", "content": feedback})
        reply = call_openai(messages)

        _, assertions = await generate_candidate_assertions([instruction, instruction_feedback], [output, reply])

        print(f'Generated assertions: {assertions}')
        assertions_str = assertions[0]

        exec(assertions_str, globals())
        assertions_code = parse_assertions(assertions_str)

        iter = 0
        
        while iter < FEEDBACK_ITERATIONS:
            tasks = []
            rows = []
            for func in ALL_FUNCTIONS:
                tasks.append(func(instruction_feedback, reply))
                rows.append({"function_code": assertions_code[func.__name__], "function_name": func.__name__})

            results = await asyncio.gather(*tasks, return_exceptions=True)

            failed_assertions = []
            for row, result in zip(rows, results):
                if isinstance(result, Exception):
                    print(f"Error: {result} from {row['function_name']}")
                    row["result"] = f"Error: {result} from {row['function_name']}"
                    continue

                row["result"] = result
                if not row["result"]:
                    failed_assertions.append(row["function_code"])
            print(f'Iteration {iter} check results: {rows}')

            if all([isinstance(row["result"], bool) and row['result'] for row in rows]):
                break

            messages.append({"role": "assistant", "content": reply})

            failed_assertions_str = '\n'.join(failed_assertions)
            messages.append({"role": "user", "content": REFLECTION_PROMPT.format(failed_assertions=failed_assertions_str)})

            reply = call_openai(messages)
            iter += 1

        if iter == FEEDBACK_ITERATIONS:
            return None
        return reply
    
    def extract_rules_from_feedback(self, messages, output, preferred_output):
        messages.append({"role": "assistant", "content": output})
        messages.append({"role": "user", "content": EXTRACT_RULE_PROMPMT.format(preferred_output=preferred_output)})
        reply = call_openai(messages)

        raw_rules = reply.split('\n')
        valid_rules = []
        for rule in raw_rules:
            lower_rule = rule.lower()
            if len(rule) >= 10 and 'If' in rule and 'then' in lower_rule:
                secs = rule.split('If')
                ls = len(secs[0])
                valid_rules.append(rule[ls:])

        return valid_rules

    def user_input(self, placeholder):
        if USERINPUTREADFROMFILE:
            print('='*10 + 'USER FEEDBACK: ' + placeholder, flush=True)  # 参与前端逻辑，不能修改
            while True:
                try:
                    with open(DIAGNOSE_USER_FEEDBACK_PATH, 'r+') as f:
                        content = f.read().strip()
                        if len(content) > 0:
                            input_content = content
                            # 清空文件内容
                            f.seek(0)
                            f.truncate()
                            break
                        else:
                            time.sleep(1)
                except Exception as err:
                    print('Error: ', err, flush=True)
                    time.sleep(1)
        else:
            input_content = input(placeholder)
        return input_content

    def interact(self, instruction, res):
        print('='*10 + 'INPUT' + '='*10)
        print(self.conversation_history)
        print('='*10 + 'OUTPUT' + '='*9)
        print(res)
        print('='*25)
        feedback = self.user_input('Please input your feedback of the D-Bot response.\n')
        print(f'Feedback: {feedback}')

        if feedback.strip() == '':
            return None
        
        refined_reply = pool.submit(asyncio.run, self.feedback(copy.deepcopy(self.conversation_history), instruction, res['content'], feedback)).result()

        if refined_reply is not None:
            print('='*6 + 'REFINED OUPUT' + '='*6)
            print(refined_reply)
            print('=' * 25)
            eval = self.user_input('Are you satisfied with our refined response? Please answer yes or no.\n')
            if eval.lower() != 'yes':
                refined_reply = self.user_input('Please input your preferred response in details.\n')
        else:
            refined_reply = self.user_input('We are sorry that we cannot refine our response based on your feedback. Please input your preferred response in details.\n')

        return refined_reply

    def remove_conflict_identical(self, new_doc, relevant_doc):
        flag = 0
        doc_rules = relevant_doc.metadata['rules'].split('\n')
        new_rules = new_doc.metadata['rules'].split('\n')
        
        tokenized_rules = [vr.split() for vr in doc_rules]
        bm25_rules = BM25Okapi(tokenized_rules)

        similar_rules = []
        for new_rule in new_rules:
            sim_rules = bm25_rules.get_top_n(new_rule.split(), doc_rules, n=1)
            similar_rules.append(sim_rules[0])

        logging.info('Checking Rules ... ')
        for new_rule, sim_rule in zip(new_rules, similar_rules):
            
            logging.info('Checking Incoming Rule: ' + new_rule)
            logging.info('Most Similar Rule: ' + sim_rule)

            keep = True
            
            if keep:
                logging.info('Check Conflict')
                rel = 'contradictory'
                messages = [{'role': 'user', 'content': compare_rules(new_rule, sim_rule, COMPARE_CONTRADICTORY_PROMPT)}]
                reply = call_openai(messages) 

                answer = reply.replace('assistant', '').replace(':', '').strip().lower()
                if 'contradictory' in answer and 'not' not in answer: keep = False

            if keep and new_doc.page_content == relevant_doc.page_content:
                logging.info('Check Identical')
                rel = 'identical'
                messages = [{'role': 'user', 'content': compare_rules(new_rule, sim_rule, COMPARE_IDENTICAL_PROMPT)}]
                reply = call_openai(messages) 

                answer = reply.replace('assistant', '').replace(':', '').strip().lower()
                if 'identical' in answer and 'not' not in answer: keep = False
            
            if not keep:
                logging.info('*****Rule Out*****')
                logging.info('Incoming Rule: ' + new_rule)
                logging.info('Out Rule: ' + sim_rule)
                logging.info('Out by ' + rel)
                logging.info('******************')
                
                doc_rules.remove(sim_rule)
        
        updated_doc = copy.deepcopy(relevant_doc)
        if new_doc.page_content == relevant_doc.page_content:
            updated_doc.metadata['rules'] = '\n'.join(new_rules + doc_rules)
            flag = 1
        else:
            updated_doc.metadata['rules'] = '\n'.join(doc_rules)
        if len(updated_doc.metadata['rules']) == 0:
            self.kb.delete_docs([updated_doc])
        else:
            self.kb.update_docs([updated_doc])
        return flag

    def parse(self):
        mark_idx = classify(self.conversation_history)
        vars, instruction = parse_messages(self.conversation_history, mark_idx=mark_idx)
        if vars is None:
            return super().parse()
        
        try:
            relevant_docs = self.kb.search_docs(vars, metadata_filter={'task': mark_idx}, top_k=1)
            if len(relevant_docs) > 0:
                relevant_rules = '\n'.join([doc.metadata['rules'] for doc in relevant_docs])
                messages_backup = copy.deepcopy(self.conversation_history)
                assert self.conversation_history[-1]["role"] == "user"
                self.conversation_history[-1]['content'] += f"\n\nIn the following, we show you some rules that may help you improve your response:\n{relevant_rules}"
            
            res = super().parse()
            if len(relevant_docs) > 0:
                self.conversation_history = messages_backup
            refined_reply = self.interact(instruction, res)

            if refined_reply is None:
                return res
            
            rules = self.extract_rules_from_feedback(copy.deepcopy(self.conversation_history), res['content'], refined_reply)

            flag = 0
            new_doc = Document(page_content=vars, metadata={'rules': '\n'.join(rules), 'task': mark_idx, 'source': str(mark_idx) + vars})
            if len(relevant_docs) > 0:
                for doc in relevant_docs:
                    flag += self.remove_conflict_identical(new_doc, doc)
            if flag == 0:
                self.kb.add_docs([new_doc])
                
            res['content'] = refined_reply
        except Exception as e:
            logging.error(e)

        return res



