import inspect
import json
import math
import os
import re
import sys
import time
from typing import Any
from typing import Dict
from typing import List
from typing import Union
from tqdm import tqdm

import random
import re
import torch
import pdb
import numpy as np

import bmtrain as bmt

from .cpm.arguments import get_args
from .cpm.llama.models import Llama
from .cpm.llama.models import LlamaConfig
from transformers import AutoTokenizer
from .cpm.llama.training_tasks import FinetuneDataset, MixedDataset
from .cpm.llama.generation import LlamaBeamSearch
from .cpm.utils import allgather_objects
from .cpm.utils import logger
from .cpm.utils import LogManager

from pydantic import BaseModel, Field

def get_tokenizer(args):
    tokenizer = AutoTokenizer.from_pretrained(args.vocab, 
                                            unk_token="<unk>",
                                            bos_token="<s>",
                                            eos_token="</s>")
    return tokenizer


def get_model(args):
    config = LlamaConfig.from_json_file(args.model_config)
    if args.flash == "none":
        config.use_flash_attn = False
    else:
        config.use_flash_attn = True
        if args.flash == "1d":
            config.flash_attn_mask_shape = "1d"
        else:
            config.flash_attn_mask_shape = "2d"
            if args.flash == "triton":
                config.flash_impl = "triton"
            elif args.flash == "cuda":
                config.flash_impl = "cuda"
    model = Llama(config)
    if args.load is not None:
        bmt.print_rank("args.load is not None, start to load checkpoints " + args.load)
        bmt.load(model, args.load)
    else:
        bmt.print_rank("args.load is None, start to initialize parameters")
        bmt.init_parameters(model)
    return model

def setup_model(args):

    start = time.time()
    model = get_model(args)
    logger.info("load model in {:.2f}s".format(time.time() - start))

    start = time.time()
    tokenizer = get_tokenizer(args)
    bmt.synchronize()
    logger.info("load tokenizer in {:.2f}s".format(time.time() - start))

    return tokenizer, model


def initialize(args):
    if "checkpointing" in inspect.signature(bmt.init_distributed).parameters:
        bmt.init_distributed(checkpointing=False, seed=args.seed)
    else:
        bmt.init_distributed(seed=args.seed)

def reformat_messages(messages):
    """set your data format"""
    assert messages[0]["role"] == "system"
    instruction = "<s>[INST] <<SYS>>\n {} \n<</SYS>>\n\n ".format(messages[0]["content"])
    state = 0
    loop_messages = messages[1:]
    for i,message in enumerate(loop_messages):
        if state == 0:
            assert message["role"] == "user", messages
            instruction += message["content"] + " [/INST] "
            state = 1
        elif state == 1:
            assert message["role"] in ["assistant", "function"]
            if message["role"] == "function":
                instruction += "\n\n<<FUNC>>\n " + message["content"] + " \n<</FUNC>>"
                if i < len(loop_messages) - 1 and loop_messages[i + 1]["role"] == "user":
                    instruction += " </s><s>[INST] "
                    state = 0
                else:
                    assert i == len(loop_messages) - 1 or loop_messages[i + 1]["role"] == "assistant"
                    instruction += "\n\n "
            elif message["role"] == "assistant":
                instruction += message["content"] 
                if loop_messages[i + 1]["role"] == "user":
                    instruction += " </s><s>[INST] "
                    state = 0
                else:
                    assert loop_messages[i + 1]["role"] == "function", messages
                    instruction += " "

    return {"input": instruction}

class LlamaInference:
    def __init__(self, args):
        self.args = args
        self.tokenizer = None
        self.model = None

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
        content = content.replace("Here is the conversation history\n\n\nHere is the execution log of tools\n\n\n", "")
        return content
    
    def process_review(self, messages):
        instruction = "You will be given some diagnosis results. Your task involves reviewing them and giving necessary advice to correct the unclear diagnosis and proposed solutions. The review should use markdown format.\n\nINPUT diagnosis results: \n"
        i = 1
        for message in messages[1:-1]:
            assert message["role"] == "assistant"
            instruction += "Diagnosis {}: #### " + message["content"] + "\n\n"
            i += 1
        assert messages[-1]["role"] == "user"
        instruction += messages[-1]["content"]
        if not instruction.endswith("."):
            instruction = instruction + "."
        return [messages[0], {"role": "user", "content": instruction}]

    def process_advice(self, messages):
        prompt = ""
        i = 1
        for message in messages:
            assert message["role"] == "assistant", message
            content = message["content"]
            if not content.startswith("##"):
                content = "## " + content
            prompt += "Advice {}: ".format(i) + content + "\n\n"
            i += 1
        return prompt

    def process_solution(self, messages):
        instruction = "You are writing a report to summarize the proposed solutions of anomaly diagnosis results. You will be given a diagnosis report with root cause diagnosis and proposed solutions. You will also be given some review advice. Your task involves summarizing the given review advice and refining the solution part of diagnosis report based on the advice.\n\nINPUT root cause analysis:\n"

        assert messages[-2]["role"] == "user"
        origin_report = messages[-2]["content"]
        old_instruction = "You are writing a report. Please summarize the refined anomaly diagnosis based on the above review advice. The anomaly diagnosis is as follows:"
        assert origin_report.startswith(old_instruction), origin_report
        origin_report = origin_report[len(old_instruction):].strip()
        origin_report = origin_report.split("===")[0].strip()
        instruction += origin_report + "\n\nINPUT solutions: \n"

        assert messages[-1]["role"] == "user"
        origin_report = messages[-1]["content"]
        old_instruction = "You are writing a report. Please summarize the refined solutions based on the above review advice. The solutions are as follows:"
        assert origin_report.startswith(old_instruction), origin_report
        origin_report = origin_report[len(old_instruction):].strip()
        origin_report_splits = origin_report.split("===")
        origin_report = origin_report_splits[0].strip()
        tail = origin_report_splits[1].strip()
        instruction += origin_report + "\n\nINPUT review advice: \n"

        instruction += self.process_advice(messages[1:-2])
        
        instruction += tail
        return [messages[0], {"role": "user", "content": instruction}]

    def process_refine(self, messages):
        instruction = "You are writing a report to summarize the root causes of anomaly diagnosis results. You will be given a diagnosis report and some review advice. Your task involves summarizing the given review advice and refining the diagnosis report based on the advice.\n\nINPUT report: \n"

        assert messages[-1]["role"] == "user"
        origin_report = messages[-1]["content"]
        old_instruction = "You are writing a report. Please summarize the refined anomaly diagnosis based on the above review advice. The anomaly diagnosis is as follows:"
        assert origin_report.startswith(old_instruction), origin_report
        origin_report = origin_report[len(old_instruction):].strip()
        origin_report_splits = origin_report.split("===")
        assert len(origin_report_splits) == 2
        origin_report = origin_report_splits[0].strip()
        tail = origin_report_splits[1].strip()
        instruction += origin_report + "\n\nINPUT review advice: \n"

        instruction += self.process_advice(messages[1:-1])

        instruction += tail
        return [messages[0], {"role": "user", "content": instruction}]
    
    def classify(self, messages):
        marks = ["Please describe the following anomaly event in natural language:", "Please give a title for the following anomaly event within 15 words:", "You are mento-carlo-choice-GPT.", "Remember that you are performing a mento-carlo search.", "Please provide a searchable summary of the input", "Please review the above diagnosis results, ", "Please summarize the refined solutions based on the above review advice.", "Please summarize the refined anomaly diagnosis based on the above review advice.", "Now you need to select experts with diverse identity to correctly analyze the root causes of the given alert.", "You can respond as follows to use tool:"]

        for idx,mark in enumerate(marks):
            for message in messages:
                content = message["content"]
                if mark in content:
                    return idx
        assert False, messages

    def inference(self, messages, max_in_len, max_length, beam_size):
        if self.model is None:
            initialize(self.args)
            self.tokenizer, self.model = setup_model(self.args)
            bmt.print_rank("finish loading")
        
        beam_search = LlamaBeamSearch(
            model=self.model,
            tokenizer=self.tokenizer,
            max_in_len=max_in_len
        )

        input = reformat_messages(messages)
        output = beam_search.generate([input], max_length=max_length, beam_size=beam_size)[0]
        output = output.replace("</s>", "").strip()
        return output

class DiagLlamaArgs(BaseModel):
    load: str = Field(default="xxxx/DiagLlama.pt")
    model_config: str = Field(default="xxxx/llama2-13b/config.json")
    vocab: str = Field(default="xxxx/llama2-13b")
    seed: int = Field(default=1234)
    flash: str = Field(default="none")

llama_inference = LlamaInference(DiagLlamaArgs())