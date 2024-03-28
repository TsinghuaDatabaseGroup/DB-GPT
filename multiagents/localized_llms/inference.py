import re
import time
import re
import logging
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.generation.utils import GenerationConfig

class Inference:
    def __init__(self, args):
        self.args = args
        self.tokenizer = None
        self.model = None

    def setup_model(self):
        start = time.time()
        model = self.get_model()
        logging.info("load model in {:.2f}s".format(time.time() - start))

        start = time.time()
        tokenizer = self.get_tokenizer()
        logging.info("load tokenizer in {:.2f}s".format(time.time() - start))

        return tokenizer, model

    def reformat(self, s):
        s = re.sub(r"\*\*\*+\s*", "```", s)
        s = re.sub(r"\s*\=\=\=\=+\s*", "===", s)
        s = re.sub(r"(\\)+'", "'", s)
        s = re.sub(r"(\\)+n", "\n", s)
        s = re.sub(r"(\\)+\n", "\n", s)
        s = re.sub(r"\n\s+\n", "\n\n", s)
        s = re.sub(r"(\\)+t", "\t", s)
        s = re.sub(r"\n\s*\n(\s*\n)+", "\n\n", s)
        return s

    def preprocess(self, content):
        content = self.reformat(content)
        return content
    
    def refine_messages(self, messages, task):
        if task in ['expert_root_cause', 'expert_solution']:
            return [messages[0], {"role": "user", "content": 'Diagnosed Root Causes: ' + messages[1]["content"] + '\n\n' + messages[2]["content"]}]
        
        if task == 'review':
            if messages[1]["role"] != "assistant":
                return messages
            
            return [messages[0], {"role": "user", "content": '# Diagnosis Results\n\n' + '\n\n'.join([m["content"] for m in messages[1:]])}]
            
        if task in ['refine_solution', 'refine_root_cause', 'label']:
            return [messages[0], {"role": "user", "content": '\n\n'.join([m["content"] for m in messages[1:]])}]
            
        # Merge continuous assistant messages to one.
        new_messages = []
        cnt = 0
        contents = []
        flag = False
        for message in messages:
            if message["role"] == "assistant":
                cnt += 1
                if len(contents) > 0 and contents[-1].startswith("Thought: ") and contents[-1].find("Observation: ") == -1:
                    contents[-1] += "\nObservation: " + message["content"]
                else:
                    contents.append(message["content"])
            else:
                if cnt > 0:
                    new_messages.append({"role": "assistant", "content": "\n\n".join(contents)})
                    flag |= (cnt > 1)
                cnt = 0
                contents = []
                new_messages.append(message)
        if cnt > 0:
            new_messages.append({"role": "assistant", "content": "\n\n".join(contents)})
            flag |= (cnt > 1)
        return new_messages if flag else messages

    def get_model(self):
        raise NotImplementedError
    
    def get_tokenizer(self):
        raise NotImplementedError
    
    def inference(self, messages, generation_config=None):
        raise NotImplementedError
    
class BaichuanInference(Inference):
    def get_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(self.args.load, trust_remote_code=True)
        return tokenizer

    def get_model(self):
        model = AutoModelForCausalLM.from_pretrained(self.args.load, device_map="auto",trust_remote_code=True)
        model.generation_config = GenerationConfig.from_pretrained(self.args.load)
        return model

    def inference(self, messages, generation_config=None):
        if self.model is None:
            self.tokenizer, self.model = self.setup_model()
        
        cur_generation_config = self.model.generation_config
        if generation_config is not None:
            for k, v in generation_config.items():
                cur_generation_config[k] = v
        
        logging.debug(str(messages))
        output = self.model.chat(self.tokenizer, messages, generation_config=cur_generation_config)
        logging.debug(output)
        return output
    
class LlamaInference(Inference):
    def get_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(self.args.load)
        return tokenizer

    def get_model(self):
        model = AutoModelForCausalLM.from_pretrained(self.args.load, device_map="auto")
        model.generation_config = GenerationConfig.from_pretrained(self.args.load)
        return model

    def inference(self, messages, generation_config=None):
        if self.model is None:
            self.tokenizer, self.model = self.setup_model()
        
        cur_generation_config = self.model.generation_config
        if generation_config is not None:
            for k, v in generation_config.items():
                cur_generation_config[k] = v
        
        logging.debug(str(messages))
        output = self.model.chat(self.tokenizer, messages, generation_config=cur_generation_config)
        logging.debug(output)
        return output

class DiagBaichuan2Args(BaseModel):
    load: str = Field(default="curtis-sun/diag-baichuan2")

class DiagBaichuan2_4bitArgs(BaseModel):
    load: str = Field(default="curtis-sun/diag-baichuan2-4bit")

class DiagLlama2Args(BaseModel):
    load: str = Field(default="curtis-sun/diag-llama2")

class DiagCodeLlamaArgs(BaseModel):
    load: str = Field(default="curtis-sun/diag-codellama")

baichuan2_inference = BaichuanInference(DiagBaichuan2Args())

baichuan2_4bit_inference = BaichuanInference(DiagBaichuan2_4bitArgs())

llama2_inference = LlamaInference(DiagLlama2Args())

codellama_inference = LlamaInference(DiagCodeLlamaArgs())