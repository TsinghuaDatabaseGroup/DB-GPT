from multiagents.localized_llms.inference import Inference
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from pydantic import BaseModel, Field
from typing import List, Union, Optional
import logging
import time
import json
import os


def classify(messages):
    marks = ["Please describe the following anomaly event in natural language:",
             "Please give a title for the following anomaly event within 15 words:",
             "You are mento-carlo-choice-GPT.",
             "Remember that you are performing a mento-carlo search.",
             "Analyze the diagnosed root causes based on above discussions in details.",
             "Give the solutions only based on above messages in details.",
             "Please provide a searchable summary of the input",
             "Please review the above diagnosis results, ",
             "Please optimize the following solutions based on the above review advice.",
             "Please give the refined root cause analysis based on the above review advice.",
             "Output all the labels mentioned in the description.",
             "Now you need to select experts with diverse identity to correctly analyze the root causes of the given alert.",
             "你的分析必须基于以下步骤"]

    for idx, mark in enumerate(marks):
        for message in messages:
            content = message["content"]
            if mark in content:
                return idx
    assert False, messages


class QwenLocalArgs(BaseModel):
    load: str = Field(default="Qwen/Qwen1.5-14B-Chat-AWQ")
    max_length: int = 32768
    top_k: int = Field(default=1)
    stop_words: List[str] = Field(default=['Observation:', 'Observation:\n'])
    pad_token_id: int = 151645


class QwenLocalInference(Inference):
    def get_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(self.args.load)
        tokenizer.pad_token_id = tokenizer.eos_token_id
        return tokenizer

    def get_model(self):
        model = AutoModelForCausalLM.from_pretrained(self.args.load, device_map="auto")
        generation_config = GenerationConfig.from_pretrained(self.args.load)
        generation_config.update(**self.args.dict())

        model.generation_config = generation_config
        return model

    def inference(self, messages):
        if self.model is None:
            self.tokenizer, self.model = self.setup_model()

        logging.debug(str(messages))
        output = self.text_completion(messages)
        logging.debug(output)
        return output

    def text_completion(self, messages) -> str:
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(**model_inputs)
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        for stop_str in self.args.stop_words:
            idx = response.find(stop_str)
            if idx != -1:
                response = response[:idx]
        return response



# 用vllm部署的服务，入参参考
# https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/openai/protocol.py
class QwenServerArgs(BaseModel):
    base_url: str = Field(default="http://127.0.0.1:8000/v1")
    api_key: str = Field(default="EMPTY")
    model: str = Field(default="/root/autodl-tmp/models/Qwen1.5-14B-Chat/")
    stop: Optional[Union[str, List[str]]] = Field(default=['Observation:', 'Observation:\n'])
    temperature: float = Field(default=0)


class QwenServerInference(Inference):
    def __init__(self, args: QwenServerArgs):
        super(QwenServerInference, self).__init__(args)
        import openai
        self.client = openai.OpenAI(base_url=args.base_url, api_key=args.api_key)

    def inference(self, messages):
        response = self.client.chat.completions.create(
            model=self.args.model,
            messages=messages,
            temperature=self.args.temperature,
            stop=self.args.stop
        )

        output = response.choices[0].message.content

        if not os.path.exists(r"saved_msg_qwen"):
            os.mkdir(r"saved_msg_qwen")
        saved_msgs = messages + [{'role': "assistant", "content": output}]
        with open(f"saved_msg_qwen/msg_{time.strftime('%H_%M_%S', time.localtime())}.json",
                  "w", encoding='utf8') as f:
            json.dump(saved_msgs, f, ensure_ascii=False, indent=4)

        return output


qwen2_local_inference = QwenLocalInference(QwenLocalArgs())
qwen2_server_inference = QwenServerInference(QwenServerArgs())
