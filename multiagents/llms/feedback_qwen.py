from . import llm_registry
from .qwen_vllm import QwenVllmChat
from .doc_kb import DocKnowledgeBase
from .feedback_openai import get_cur_task, get_time
import copy
from multiagents.utils.interact import (user_input, add_display_message, add_edit_message, add_feedback_message,
                                        finish_feedback_message, finish_select_edit_message)

# EXTRACT_RULE_PROMPT_zh = """我对你之前的回复不太满意。现在给你一个我更喜欢的回复，请比较它们的差异，并总结成规则，以便你以后能给出更好的回复。
# 要求如下：
# 1. 规则必须按照\"如果...，则...\"的模板。
# 2. 如果有多条独立的规则，一条一条给出。
# 3. 直接给出规则的内容，不要说多余的话。
# 4. 保证规则的准确和简洁。
# 下面是我更喜欢的回复：
# {preferred_output}
# """

JUDGE_FEEDBACK_PROMPT_zh = "你将收到用户对回复的反馈。请判断它是否包括任何关于如何改进回复内容或格式的建议。\n只回答是或否。"


@llm_registry.register('feedback_qwen')
class FeedbackQwenChat(QwenVllmChat):
    kb: DocKnowledgeBase = None
    feedbacks: list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.enable_feedback = True
        self.kb = DocKnowledgeBase(knowledge_base_name='feedback_qwen')

    def feedback(self, messages, instruction, output, feedback):
        """根据人类反馈，模型生成更好的回答"""
        messages = copy.deepcopy(messages)
        # instruction_feedback = f'{instruction}\n\n{feedback}'
        messages.append({"role": "assistant", "content": output})
        messages.append({"role": "user", "content": feedback})
        reply = self.chat(messages)

        return reply

    def extract_rules_from_feedback(self, messages, output, preferred_output):
        """从人类反馈，模型生成了更好的回答，抽取出原始回答和更好回答的差异规则。"""
        raise NotImplementedError

    def judge_feedback(self, feedback):
        """调用大模型判断人类反馈是否有价值"""
        judge_messages = [{'role': 'system', 'content': JUDGE_FEEDBACK_PROMPT_zh},
                          {'role': 'user', 'content': feedback}]
        reply = self.chat(judge_messages)
        return "是" in reply

    def interact(self, instruction, res, role, task):
        """用户交互"""
        cur_task = get_cur_task(task)
        print('=' * 10 + 'INPUT' + '=' * 10, flush=True)
        print(self.conversation_history, flush=True)
        print('=' * 10 + 'OUTPUT' + '=' * 9, flush=True)
        print(res, flush=True)
        print('=' * 25, flush=True)
        feedback_placeholder = "请输入你对D-Bot回复的反馈（例如：你必须按xxx格式回复；关于xxx，你应该提供更多细节）。"
        add_feedback_message(cur_task, role, feedback_placeholder, res['content'], get_time())
        feedback = user_input(feedback_placeholder + '\n')
        finish_feedback_message()
        if feedback.strip() == '' or feedback.lower() == 'continue' or not self.judge_feedback(feedback):
            empty_feedback_placeholder = '没有/无效反馈，诊断继续。'
            add_display_message(cur_task, role, empty_feedback_placeholder, get_time())
            return None

        refined_reply = self.feedback(self.conversation_history, instruction, res['content'], feedback)

        if refined_reply is not None:
            print('=' * 6 + 'REFINED OUTPUT' + '=' * 6, flush=True)
            print(refined_reply, flush=True)
            print('=' * 25, flush=True)
            eval_placeholder = "你对改进的回答满意吗？请只回答“是”或“否”。"
            add_feedback_message(cur_task, role, eval_placeholder, refined_reply, get_time())
            eval_ = user_input(eval_placeholder + '\n')
            finish_feedback_message()
            if "否" in eval_:
                refine_placeholder = '请详细输入你认为正确的回答。'
                add_edit_message(cur_task, role, refine_placeholder, res['content'], get_time())
                refined_reply = user_input(refine_placeholder + '\n')
                self.feedbacks.append(
                    {"feedback": feedback, "refined_response": refined_reply, "auto": False, "task": task})
                finish_select_edit_message(cur_task, role)
            else:
                self.feedbacks.append(
                    {"feedback": feedback, "refined_response": refined_reply, "auto": True, "task": task})
                finish_feedback_message()
        else:
            print('=' * 10 + 'OUTPUT' + '=' * 9, flush=True)
            print(res, flush=True)
            print('=' * 25, flush=True)
            refine_placeholder = "很抱歉我们无法基于你的反馈改进回答。请详细输入你认为正确的回答。"
            add_edit_message(cur_task, role, refine_placeholder, res['content'], get_time())
            refined_reply = user_input(refine_placeholder + '\n')
            self.feedbacks.append(
                {"feedback": feedback, "refined_response": refined_reply, "auto": False, "task": task})
            finish_select_edit_message(cur_task, role)

        return refined_reply

    def remove_conflict_identical(self, new_doc, relevant_doc):
        """去除矛盾、重复的规则"""
        raise NotImplementedError

    def parse(self, role="", task=""):
        res = super().parse(role=role, task=task)

        if task in ['expert_root_cause', 'expert_solution', 'review', 'refine_root_cause', 'refine_solution']:
            refined_reply = self.interact("", res, role, task)
            if refined_reply is not None:
                res['content'] = refined_reply

        return res
