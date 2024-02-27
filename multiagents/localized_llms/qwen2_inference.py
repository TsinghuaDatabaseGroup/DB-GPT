from multiagents.localized_llms.inference import Inference
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from pydantic import BaseModel, Field
from typing import List
import logging


def text_completion(model, tokenizer, messages, stop_words: List[str], generate_config=None) -> str:
    if generate_config is None:
        generate_config = {}
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(**model_inputs, **generate_config)
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    for stop_str in stop_words:
        idx = response.find(stop_str)
        if idx != -1:
            response = response[: idx + len(stop_str)]
    return response


class QwenLocalArgs(BaseModel):
    load: str = Field(default="Qwen/Qwen1.5-14B-Chat-AWQ")
    max_length: int = 32768
    top_k: int = Field(default=1)
    stop_words: List[str] = Field(default=['Observation:', 'Observation:\n'])
    pad_token_id: int = 151645


class QwenServerArgs(BaseModel):
    base_url: str = Field(default="http://127.0.0.1:8000/v1")
    api_key: str = Field(default="EMPTY")
    temperature: float = Field(default=0)


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

    def inference(self, messages, generation_config=None):
        if self.model is None:
            self.tokenizer, self.model = self.setup_model()

        logging.debug(str(messages))
        output = text_completion(self.model, self.tokenizer, messages, self.args.stop_words, **generation_config)
        logging.debug(output)
        return output


class QwenServerInference(Inference):
    def __init__(self, args: QwenServerArgs):
        super(QwenServerInference, self).__init__(args)
        import openai
        self.client = openai.OpenAI(base_url=args.base_url, api_key=args.api_key)

    def inference(self, messages, generation_config=None):
        output = self.client.chat.completions.create(
            messages=messages,
            temperature=self.args.temperature,
            **generation_config
        )
        return output


qwen2_local_inference = QwenLocalInference(QwenLocalArgs())
qwen2_server_inference = QwenServerInference(QwenServerArgs())
