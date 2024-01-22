from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import bmtrain as bmt
import numpy as np
import torch
import torch.nn.functional as F
import logging

from ...generation import apply_repetition_penalty
from ...generation import BeamHypotheses
from ...generation import top_k_top_p_filtering

# from ..training_tasks.llama.pretrain import convert_data_to_id
from ...utils import pad, allgather_objects
from ..models import LlamaTorch
from ..tokenizers.llama import LlamaTokenizer

def build_chat_input(tokenizer, messages):
    """set your data format"""
    assert messages[0]["role"] == "system"
    instruction = "<s>[INST] <<SYS>>\n {sys_message} \n<</SYS>>\n\n ".format(sys_message=messages[0]["content"])
    state = 0
    loop_messages = messages[1:]
    for i,message in enumerate(loop_messages):
        if state == 0:
            assert message["role"] == "user", messages
            instruction += message["content"] + " [/INST] "
            state = 1
        elif state == 1:
            assert message["role"] == "assistant"
            instruction += message["content"] 
            if i < len(loop_messages) - 1:
                assert loop_messages[i + 1]["role"] == "user", messages
                instruction += " </s><s>[INST] "
                state = 0
            else:
                instruction += "\n\n"

    return tokenizer.encode(instruction)


class LlamaGeneration:
    def __init__(self, model: LlamaTorch, tokenizer: LlamaTokenizer, max_in_len=1024, use_nbce: bool = False):
        model.eval()
        self.model = model
        self.tokenizer = tokenizer
        self.max_in_len = max_in_len

    def _convert_to_tensors(self, data: Any):
        input_ids = build_chat_input(self.tokenizer, data["input"])
        if len(input_ids) > self.max_in_len:
            logging.warn(f"Token indices sequence length is longer than the specified maximum sequence length for this generation ({len(input_ids)} > {self.max_in_len}).")
        
        model_input = {}

        model_input["input_ids"] = torch.tensor(input_ids[: self.max_in_len], dtype=torch.int32).unsqueeze(0)
        model_input["context"] = torch.zeros(
            (model_input["input_ids"].shape[0], model_input["input_ids"].shape[1]), dtype=torch.int16
        )
        model_input["span"] = torch.ones((model_input["input_ids"].shape[1],), dtype=torch.int16).unsqueeze(0)
        model_input["length"] = torch.tensor([model_input["input_ids"].shape[1]], dtype=torch.int16).unsqueeze(0)
        return model_input

    def _process_list(self, data_list: List[Any]):
        input_tensors = list(map(self._convert_to_tensors, data_list))
        keys = set(input_tensors[0].keys())
        padded = {}
        for key in keys:
            padded[key] = pad(input_tensors, key, padding_side="left").cuda()
        return padded

    def generate(self, data_list, **kwargs):
        origin_data_list = data_list.copy()
        model_inputs = self._process_list(data_list)
        with torch.inference_mode():
            result_ids = self._decode(model_inputs, **kwargs)

        return result_ids

    def _decode(self, model_inputs, **kwargs):
        raise NotImplementedError("_decode is not implemented.")


class LlamaBeamSearch(LlamaGeneration):
    def _decode(
        self,
        model_inputs,
        beam_size=4,
        max_length=100,
        repetition_penalty=1.2,
        repetition_window=None,
    ):
        """
        Beam search
        Args:
            model_inputs (dict): input ids.
            beam_size (int, optional, defaults to 3): beam size of beam search.
            generate_length (int, optional, defaults to 100): maximum generation length.
            repetition_penalty (float, optional, defaults to 1.0): repetition penalty coefficient, 1.0 means no penalty.
            repetition_window (int, optional, defaults to None): window size of repetition penalty, None means that all output tokens are penalized.
        """  # noqa: E501
        # generate_length + 1 for EOS token
        max_length += 1
        # expand dimmension
        batch_size = model_inputs["input_ids"].size(0)
        input: torch.Tensor = (
            model_inputs["input_ids"]
            .unsqueeze(1)
            .expand(batch_size, beam_size, -1)
            .contiguous()
            .view(batch_size * beam_size, -1)
        )
        length = (
            model_inputs["length"]
            .squeeze(1)
            .unsqueeze(1)
            .expand(batch_size, beam_size)
            .contiguous()
            .view(
                batch_size * beam_size,
            )
        )
        span: torch.Tensor = (
            model_inputs["span"]
            .unsqueeze(1)
            .expand(batch_size, beam_size, -1)
            .contiguous()
            .view(batch_size * beam_size, -1)
        )
        context: torch.Tensor = (
            model_inputs["context"]
            .unsqueeze(1)
            .expand(batch_size, beam_size, -1)
            .contiguous()
            .view(batch_size * beam_size, -1)
        )

        done = [False for _ in range(batch_size)]

        beam_scores = torch.zeros((batch_size, beam_size), dtype=torch.float, device=input.device)
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view(-1)

        # generated hypotheses
        generated_hyps = [
            BeamHypotheses(beam_size, max_length, length_penalty=1, early_stopping=False) for _ in range(batch_size)
        ]

        pred_start_index = input.size(-1)
        past_key_values = None

        for i in range(max_length + 1):
            with torch.no_grad():
                if i == 0:
                    logits, _, past_key_values = self.model.inference(
                        input=input,
                        context=context,
                        span=span,
                        length=length,
                        past_key_values=past_key_values,
                    )
                else:
                    logits, _, past_key_values = self.model.inference(
                        input=input[:, -1:],
                        context=context,
                        span=span,
                        length=length,
                        past_key_values=past_key_values,
                    )
                # (batch * beam, seqlen, model_dim)
                logits = logits[:, -1, :]
            
            # skip all steps when we are done with each sentence
            if all(done):
                break

            apply_repetition_penalty(
                logits,
                batch_size,
                beam_size,
                input,
                repetition_penalty,
                pred_start_index,
                input.size(-1) - 1,
                repetition_window,
            )

            scores = F.log_softmax(logits, dim=-1)

            next_scores = scores + beam_scores[:, None].expand_as(scores)  # (batch_size * beam_size, vocab_size)

            # re-organize to group the beam together (we are keeping top hypothesis accross beams)
            next_scores = next_scores.view(batch_size, -1)  # (batch_size, beam_size * vocab_size)
            next_scores, next_words = torch.topk(next_scores, 2 * beam_size, dim=1, largest=True, sorted=True)

            assert next_scores.size() == next_words.size() == (batch_size, 2 * beam_size)
            next_batch_beam = []

            for sent_id in range(batch_size):
                # if we are done with this sentence
                done[sent_id] = done[sent_id] or generated_hyps[sent_id].is_done(next_scores[sent_id].max().item(), i)
                if done[sent_id]:
                    next_batch_beam.extend([(0, 0, 0)] * beam_size)  # pad the batch
                    continue

                # next sentence beam content
                next_sent_beam = []

                # next words for this sentence
                for idx, value in zip(next_words[sent_id], next_scores[sent_id]):
                    # get beam and word IDs
                    beam_id = torch.div(idx, scores.size(-1), rounding_mode="floor")
                    word_id = idx % scores.size(-1)

                    # end of sentence, or next word
                    if word_id == self.tokenizer.eos_token_id or i == max_length:
                        generated_hyps[sent_id].add(
                            input[sent_id * beam_size + beam_id, pred_start_index:].clone().cpu().tolist() + [word_id],
                            value.item(),
                        )
                    else:
                        next_sent_beam.append((value, word_id, sent_id * beam_size + beam_id))

                    # the beam for next step is full
                    if len(next_sent_beam) == beam_size:
                        break

                # update next beam content
                assert len(next_sent_beam) == 0 if i == max_length else beam_size
                if len(next_sent_beam) == 0:
                    next_sent_beam = [(0, 0, 0)] * beam_size  # pad the batch
                next_batch_beam.extend(next_sent_beam)
                assert len(next_batch_beam) == beam_size * (sent_id + 1)

            # we have reached the last step
            if i == max_length:
                break

            # sanity check / prepare next batch
            assert len(next_batch_beam) == batch_size * beam_size
            beam_scores = beam_scores.new([x[0] for x in next_batch_beam])
            beam_words = input.new([x[1] for x in next_batch_beam])
            beam_idx = torch.tensor([x[2] for x in next_batch_beam], device=input.device).long()
            # re-order batch and internal states
            input = input[beam_idx, :]

            past_key_values["buffer"] = [list(each) if each is not None else each for each in past_key_values["buffer"]]  # type: ignore # noqa: E501
            for key_value_layer in past_key_values["buffer"]:
                if key_value_layer is not None:
                    key_value_layer[0] = key_value_layer[0][beam_idx]
                    key_value_layer[1] = key_value_layer[1][beam_idx]

            input = torch.cat([input, beam_words.unsqueeze(1)], dim=-1)
            context = torch.cat(
                [context, context[:, -1:]],
                dim=-1,
            )
            length += 1

            span = torch.cat([span, span[:, -1:]], dim=-1)

        # select the best hypotheses

        results = []
        for i, hypotheses in enumerate(generated_hyps):
            best_hyp = max(hypotheses.hyp, key=lambda x: x[0])[1]
            results.append(best_hyp)

        result_text = list(map(self.tokenizer.decode, results))
        return result_text


class LlamaRandomSampling(LlamaGeneration):
    def _decode(
        self,
        model_inputs,
        max_length=100,
        top_k=0,
        top_p=0.9,
        temperature=0.9,
        repetition_penalty=1.0,
        repetition_window=None,
        **kwargs,
    ):
        """
        Top-k and top-p sampling.
        Args:
            model_inputs (dict): input ids
            generate_length (int, optional, defaults to 100): maximum generation length
            top_k (int, optional, defaults to 0): keep only top k tokens with highest probability. 0 means keeping all tokens.
            top_p (int, optional, defaults to 0.9): keep the top tokens with cumulative probability >= top_p.
            temperature (int, optional, defaults to 0.9): the value that can cool down the logits distribution.
            repetition_penalty (float, optional, defaults to 1.0): repetition penalty coefficient, 1.0 means no penalty.
            repetition_window (int, optional, defaults to None): window size of repetition penalty, None means that all output tokens are penalized.
        """  # noqa: E501
        # generate_length + 1 for EOS token
        max_length += 1

        input = model_inputs["input_ids"]
        context = model_inputs["context"]

        length = model_inputs["length"].squeeze(1)
        span = model_inputs["span"]
        batch_size = input.size(0)

        pred_start_index = input.size(-1)
        past_key_values = None
        done = [False for _ in range(batch_size)]
        results = [None for _ in range(batch_size)]
        for i in range(max_length):
            if i == 0:
                logits, _, past_key_values = self.model.inference(
                    input=input,
                    context=context,
                    length=length,
                    span=span,
                    past_key_values=past_key_values,
                )
            else:
                logits, _, past_key_values = self.model.inference(
                    input=input[:, -1:],
                    context=context,
                    length=length,
                    span=span,
                    past_key_values=past_key_values,
                )

            logits = logits[:, -1, :]

            apply_repetition_penalty(
                logits,
                batch_size,
                1,
                input,
                repetition_penalty,
                pred_start_index,
                input.size(-1) - 1,
                repetition_window,
            )

            logits = logits / temperature
            logits = top_k_top_p_filtering(logits, top_k=top_k, top_p=top_p)

            logits_no_eos = logits.clone()
            logits_no_eos[:, self.tokenizer.eos_id] = 0.0
            probs = F.softmax(logits, dim=-1)
            probs_no_eos = F.softmax(logits_no_eos, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            for idx in range(batch_size):
                if not done[idx] and (next_token[idx].item() == self.tokenizer.eos_token_id or i == max_length - 1):
                    done[idx] = True
                    results[idx] = input[idx, pred_start_index:].clone().cpu().tolist()  # type: ignore # noqa: E501

                if not done[idx]:
                    next_bak = torch.multinomial(probs_no_eos, num_samples=1)
                    next_token[idx] = next_bak[idx]

            if sum(done) == batch_size:
                break

            # update input ids
            input = torch.cat([input, next_token], dim=-1)
            length += 1

            context = torch.cat(
                [context, context[:, -1:]],
                dim=-1,
            )
            span = torch.cat(
                [span, span[:, -1:]],
                dim=-1,
            )

        result_text = list(map(self.tokenizer.decode, results))
        return result_text


class LlamaBeamSearchNBCE(LlamaGeneration):
    def _decode(
        self,
        model_inputs,
        beam_size=5,
        max_length=100,
        repetition_penalty=1.0,
        repetition_window=None,
    ):
        """
        Beam search
        Args:
            model_inputs (dict): input ids.
            beam_size (int, optional, defaults to 3): beam size of beam search.
            generate_length (int, optional, defaults to 100): maximum generation length.
            repetition_penalty (float, optional, defaults to 1.0): repetition penalty coefficient, 1.0 means no penalty.
            repetition_window (int, optional, defaults to None): window size of repetition penalty, None means that all output tokens are penalized.
        """  # noqa: E501
        # generate_length + 1 for EOS token
        max_length += 1

        # expand dimmension
        batch_size = model_inputs["input_ids"].size(0)
        input: torch.Tensor = (
            model_inputs["input_ids"]
            .unsqueeze(1)
            .expand(batch_size, beam_size, -1)
            .contiguous()
            .view(batch_size * beam_size, -1)
        )
        length = (
            model_inputs["length"]
            .squeeze(1)
            .unsqueeze(1)
            .expand(batch_size, beam_size)
            .contiguous()
            .view(
                batch_size * beam_size,
            )
        )
        span: torch.Tensor = (
            model_inputs["span"]
            .unsqueeze(1)
            .expand(batch_size, beam_size, -1)
            .contiguous()
            .view(batch_size * beam_size, -1)
        )
        context: torch.Tensor = (
            model_inputs["context"]
            .unsqueeze(1)
            .expand(batch_size, beam_size, -1)
            .contiguous()
            .view(batch_size * beam_size, -1)
        )

        done = [False]

        beam_scores = torch.zeros((1, beam_size), dtype=torch.float, device=input.device)
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view(-1)

        # generated hypotheses
        generated_hyps = [
            BeamHypotheses(beam_size, max_length, length_penalty=1, early_stopping=False) for _ in range(1)
        ]

        pred_start_index = input.size(-1)
        past_key_values = None

        for i in range(max_length + 1):
            if i == 0:
                logits, _, past_key_values = self.model.inference(
                    input=input,
                    context=context,
                    span=span,
                    length=length,
                    past_key_values=past_key_values,
                )
            else:
                logits, _, past_key_values = self.model.inference(
                    input=input[:, -1:],
                    context=context,
                    span=span,
                    length=length,
                    past_key_values=past_key_values,
                )
            # skip all steps when we are done with each sentence

            if all(done):
                break

            # (batch * beam, seqlen, model_dim)
            assert logits.size(0) > 1, "nbce needs to ensure that the length of logits 0 is greater than 1"
            logits = NBCE(logits)  # [vocab_size]
            logits = logits.tile(beam_size, 1)

            if i == 0:
                logits[:, self.tokenizer.bos_token_id] = -float("inf")
            apply_repetition_penalty(
                logits,
                1,
                beam_size,
                input,
                repetition_penalty,
                pred_start_index,
                input.size(-1) - 1,
                repetition_window,
            )

            scores = F.log_softmax(logits, dim=-1)

            next_scores = scores + beam_scores[:, None].expand_as(scores)  # (batch_size * beam_size, vocab_size)

            # re-organize to group the beam together (we are keeping top hypothesis accross beams)
            next_scores = next_scores.view(1, -1)  # (batch_size, beam_size * vocab_size)
            next_scores, next_words = torch.topk(next_scores, 2 * beam_size, dim=1, largest=True, sorted=True)

            assert next_scores.size() == next_words.size() == (1, 2 * beam_size)
            next_batch_beam = []

            for sent_id in range(1):
                # if we are done with this sentence
                done[sent_id] = done[sent_id] or generated_hyps[sent_id].is_done(next_scores[sent_id].max().item(), i)
                if done[sent_id]:
                    next_batch_beam.extend([(0, 0, 0)] * beam_size)  # pad the batch
                    continue

                # next sentence beam content
                next_sent_beam = []

                # next words for this sentence
                for idx, value in zip(next_words[sent_id], next_scores[sent_id]):
                    # get beam and word IDs
                    beam_id = torch.div(idx, scores.size(-1), rounding_mode="floor")
                    word_id = idx % scores.size(-1)

                    # end of sentence, or next word
                    if word_id == self.tokenizer.eos_token_id or i == max_length:
                        generated_hyps[sent_id].add(
                            input[sent_id * beam_size + beam_id, pred_start_index:].clone().cpu().tolist(),
                            value.item(),
                        )
                    else:
                        next_sent_beam.append((value, word_id, sent_id * beam_size + beam_id))

                    # the beam for next step is full
                    if len(next_sent_beam) == beam_size:
                        break

                # update next beam content
                assert len(next_sent_beam) == 0 if i == max_length else beam_size
                if len(next_sent_beam) == 0:
                    next_sent_beam = [(0, 0, 0)] * beam_size  # pad the batch
                next_batch_beam.extend(next_sent_beam)
                assert len(next_batch_beam) == beam_size * (sent_id + 1)

            # we have reached the last step
            if i == max_length:
                break

            # sanity check / prepare next batch
            assert len(next_batch_beam) == batch_size * beam_size
            beam_scores = beam_scores.new([x[0] for x in next_batch_beam])
            beam_words = input.new([x[1] for x in next_batch_beam])
            beam_idx = torch.tensor([x[2] for x in next_batch_beam], device=input.device).long()
            beam_idx *= batch_size
            # re-order batch and internal states
            input = input[beam_idx, :]

            past_key_values["buffer"] = [list(each) if each is not None else each for each in past_key_values["buffer"]]  # type: ignore # noqa: E501
            for key_value_layer in past_key_values["buffer"]:
                if key_value_layer is not None:
                    key_value_layer[0] = key_value_layer[0][beam_idx]
                    key_value_layer[1] = key_value_layer[1][beam_idx]

            input = torch.cat([input, beam_words.unsqueeze(1)], dim=-1)
            context = torch.cat(
                [context, torch.zeros((context.size(0), 1), dtype=torch.int16, device=context.device)],
                dim=-1,
            )
            length = past_key_values["buffer_length"]
            length = torch.cat(
                [length, torch.ones((length.size(0), 1), dtype=torch.int16, device=length.device)],
                dim=-1,
            )
            span = torch.cat([span, span[:, -1:]], dim=-1)

        # select the best hypotheses
        results = []
        for i, hypotheses in enumerate(generated_hyps):
            best_hyp = max(hypotheses.hyp, key=lambda x: x[0])[1]
            results.append(best_hyp)

        result_text = list(map(self.tokenizer.decode, results))
        return result_text


class LlamaRandomSamplingNBCE(LlamaGeneration):
    def _decode(
        self,
        model_inputs,
        max_length=100,
        top_k=0,
        top_p=0.9,
        temperature=0.9,
        repetition_penalty=1.0,
        repetition_window=None,
        **kwargs,
    ):
        """
        Top-k and top-p sampling.
        Args:
            model_inputs (dict): input ids
            generate_length (int, optional, defaults to 100): maximum generation length
            top_k (int, optional, defaults to 0): keep only top k tokens with highest probability. 0 means keeping all tokens.
            top_p (int, optional, defaults to 0.9): keep the top tokens with cumulative probability >= top_p.
            temperature (int, optional, defaults to 0.9): the value that can cool down the logits distribution.
            repetition_penalty (float, optional, defaults to 1.0): repetition penalty coefficient, 1.0 means no penalty.
            repetition_window (int, optional, defaults to None): window size of repetition penalty, None means that all output tokens are penalized.
        """  # noqa: E501
        # generate_length + 1 for EOS token
        max_length += 1

        input = model_inputs["input_ids"]
        context = model_inputs["context"]

        length = model_inputs["length"].squeeze(1)
        span = model_inputs["span"]
        batch_size = input.size(0)

        pred_start_index = input.size(-1)
        past_key_values = None
        done = [False]
        results = [None]
        for i in range(max_length):
            if i == 0:
                logits, _, past_key_values = self.model.inference(
                    input=input,
                    context=context,
                    length=length,
                    span=span,
                    past_key_values=past_key_values,
                )
            else:
                logits, _, past_key_values = self.model.inference(
                    input=input[:, -1:],
                    context=context,
                    length=length,
                    span=span,
                    past_key_values=past_key_values,
                )

            assert logits.size(0) > 1, "nbce needs to ensure that the length of logits 0 is greater than 1"
            logits = NBCE(logits)  # [vocab_size]
            logits = logits[None]

            if i == 0:
                logits[:, self.tokenizer.bos_token_id] = -float("inf")
                # logits[:, self.tokenizer.newline_id] = -float("inf")

            apply_repetition_penalty(
                logits,
                1,
                1,
                input,
                repetition_penalty,
                pred_start_index,
                input.size(-1) - 1,
                repetition_window,
            )

            logits = logits / temperature
            logits = top_k_top_p_filtering(logits, top_k=top_k, top_p=top_p)

            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            for idx in range(1):
                if not done[idx] and (next_token[idx].item() == self.tokenizer.eos_token_id or i == max_length - 1):
                    done[idx] = True
                    results[idx] = input[idx, pred_start_index:].clone().cpu().tolist()  # type: ignore # noqa: E501

            if sum(done) == 1:
                break
            next_token = next_token.tile(batch_size, 1)
            # update input ids
            input = torch.cat([input, next_token], dim=-1)
            length = past_key_values["buffer_length"]
            length = torch.cat(
                [length, torch.ones((length.size(0), 1), dtype=torch.int32, device=length.device)],
                dim=-1,
            )
            # length += 1
            context = torch.cat(
                [context, torch.zeros((context.size(0), 1), dtype=torch.int16, device=context.device)],
                dim=-1,
            )
            span = torch.cat(
                [span, torch.zeros((span.size(0), 1), dtype=torch.int32, device=span.device)],
                dim=-1,
            )

        result_text = list(map(self.tokenizer.decode, results))
        return result_text
