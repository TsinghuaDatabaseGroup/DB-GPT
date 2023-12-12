import inspect
import re
import time
import re
import bmtrain as bmt
import logging
from pydantic import BaseModel, Field

from .cpm.llama.models import Llama
from .cpm.llama.models import LlamaConfig
from .cpm.baichuan.models import Baichuan
from .cpm.baichuan.models import BaichuanConfig
from transformers import AutoTokenizer
from .cpm.llama.generation import LlamaBeamSearch
from .cpm.baichuan.generation.baichuan import BaichuanBeamSearch
from .cpm.utils import logger

class Inference:
    def __init__(self, args):
        self.args = args
        self.tokenizer = None
        self.model = None

    def initialize(self):
        if "checkpointing" in inspect.signature(bmt.init_distributed).parameters:
            bmt.init_distributed(checkpointing=False, seed=self.args.seed)
        else:
            bmt.init_distributed(seed=self.args.seed)

    def setup_model(self):
        start = time.time()
        model = self.get_model()
        logger.info("load model in {:.2f}s".format(time.time() - start))

        start = time.time()
        tokenizer = self.get_tokenizer()
        bmt.synchronize()
        logger.info("load tokenizer in {:.2f}s".format(time.time() - start))

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
    
    def refine_messages(self, messages, mark_idx):
        if mark_idx == 4 or mark_idx == 5:
            return [messages[0], {"role": "user", "content": 'Diagnosed Root Causes: ' + messages[1]["content"] + '\n\n' + messages[2]["content"]}]
        
        if mark_idx == 7:
            if messages[1]["role"] != "assistant":
                return messages
            
            return [messages[0], {"role": "user", "content": '# Diagnosis Results\n\n' + '\n\n'.join([m["content"] for m in messages[1:]])}]
            
        if mark_idx == 8 or mark_idx == 9 or mark_idx == 10:
            return [messages[0], {"role": "user", "content": '\n\n'.join([m["content"] for m in messages[1:]])}]
            
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
    
    def classify(self, messages):
        marks = ["Please describe the following anomaly event in natural language:", "Please give a title for the following anomaly event within 15 words:", "You are mento-carlo-choice-GPT.", "Remember that you are performing a mento-carlo search.", "Analyze the diagnosed root causes based on above discussions in details.", "Give the solutions only based on above messages in details.", "Please provide a searchable summary of the input", "Please review the above diagnosis results, ", "Please optimize the following solutions based on the above review advice.", "Please give the refined root cause analysis based on the above review advice.", "Output all the labels mentioned in the description.", "Now you need to select experts with diverse identity to correctly analyze the root causes of the given alert.", "You can respond as follows to use tool:"]

        for idx,mark in enumerate(marks):
            for message in messages:
                content = message["content"]
                if mark in content:
                    return idx
        assert False, messages

    def get_model(self):
        raise NotImplementedError
    
    def get_tokenizer(self):
        raise NotImplementedError
    
    def inference(self, messages, max_in_len, max_length, beam_size):
        raise NotImplementedError
    
class LlamaInference(Inference):
    def get_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(self.args.vocab)
        return tokenizer

    def get_model(self):
        config = LlamaConfig.from_json_file(self.args.model_config)
        if self.args.flash == "none":
            config.use_flash_attn = False
        else:
            config.use_flash_attn = True
            if self.args.flash == "1d":
                config.flash_attn_mask_shape = "1d"
            else:
                config.flash_attn_mask_shape = "2d"
                if self.args.flash == "triton":
                    config.flash_impl = "triton"
                elif self.args.flash == "cuda":
                    config.flash_impl = "cuda"
        model = Llama(config)
        if self.args.load is not None:
            bmt.print_rank("args.load is not None, start to load checkpoints " + self.args.load)
            bmt.load(model, self.args.load)
        else:
            bmt.print_rank("args.load is None, start to initialize parameters")
            bmt.init_parameters(model)
        return model

    def inference(self, messages, max_in_len, max_length, beam_size):
        if self.model is None:
            self.initialize()
            self.tokenizer, self.model = self.setup_model()
            bmt.print_rank("finish loading")
        
        beam_search = LlamaBeamSearch(
            model=self.model,
            tokenizer=self.tokenizer,
            max_in_len=max_in_len
        )

        input = {"input": messages}
        logging.debug(str(messages))
        output = beam_search.generate([input], max_length=max_length, beam_size=beam_size)[0]
        output = output.replace("</s>", "").strip()
        logging.debug(output)
        return output
    
class BaichuanInference(Inference):
    def get_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(self.args.vocab, trust_remote_code=True)
        return tokenizer


    def get_model(self):
        config = BaichuanConfig.from_json_file(self.args.model_config)
        if self.args.flash == "none":
            config.use_flash_attn = False
        else:
            config.use_flash_attn = True
            if self.args.flash == "1d":
                config.flash_attn_mask_shape = "1d"
            else:
                config.flash_attn_mask_shape = "2d"
                if self.args.flash == "triton":
                    config.flash_impl = "triton"
                elif self.args.flash == "cuda":
                    config.flash_impl = "cuda"
        model = Baichuan(config)
        if self.args.load is not None:
            bmt.print_rank("args.load is not None, start to load checkpoints" + self.args.load)
            bmt.load(model, self.args.load)
        else:
            bmt.print_rank("args.load is None, start to initialize parameters")
            bmt.init_parameters(model)
        return model

    def inference(self, messages, max_in_len, max_length, beam_size):
        if self.model is None:
            self.initialize()
            self.tokenizer, self.model = self.setup_model()
            bmt.print_rank("finish loading")
        
        beam_search = BaichuanBeamSearch(
            model=self.model,
            tokenizer=self.tokenizer,
            max_in_len=max_in_len
        )

        input = {"input": messages}
        logging.debug(str(messages))
        output = beam_search.generate([input], max_length=max_length, beam_size=beam_size)[0]
        output = output.replace("</s>", "").strip()
        logging.debug(output)
        return output

class DiagLlama2Args(BaseModel):
    load: str = Field(default="xxxx/llama2-13b/diagllama2.pt")
    model_config: str = Field(default="xxxx/llama2-13b/config.json")
    vocab: str = Field(default="xxxx/llama2/llama-13b")
    seed: int = Field(default=1234)
    flash: str = Field(default="none")

class DiagCodeLlamaArgs(BaseModel):
    load: str = Field(default="xxxx/codellama-13b/diagcodellama.pt")
    model_config: str = Field(default="xxxx/codellama-13b/config.json")
    vocab: str = Field(default="xxxx/codellama-13b")
    seed: int = Field(default=1234)
    flash: str = Field(default="none")

class DiagBaichuan2Args(BaseModel):
    load: str = Field(default="xxxx/baichuan2-13b/diagbaichuan2.pt")
    model_config: str = Field(default="xxxx/baichuan2-13b/config.json")
    vocab: str = Field(default="xxxx/baichuan2-13b")
    seed: int = Field(default=1234)
    flash: str = Field(default="none")

llama2_inference = LlamaInference(DiagLlama2Args())
codellama_inference = LlamaInference(DiagCodeLlamaArgs())
baichuan2_inference = BaichuanInference(DiagBaichuan2Args())