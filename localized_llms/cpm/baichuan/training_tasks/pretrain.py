# coding=utf-8
# Copyright 2022 The OpenBMB team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib.machinery
import importlib.util
import json
import multiprocessing
import os
import random
import time
import types
from collections import OrderedDict
from queue import Empty
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

import bmtrain as bmt
import numpy as np
import torch
from numpy.typing import NDArray
from typing_extensions import TypedDict

from ...dataset import DistributedDataset
from ..tokenizers import BaichuanTokenizer


class _MixedDatasetConfig(TypedDict):
    weight: float
    path: str
    transforms: Union[List[Dict[str, Any]], str]
    task_name: str
    dataset_name: str
    incontext_weight: List[float]
    lines: int
    dataset: DistributedDataset


BaichuanInputType = Union[str, Dict[str, "BaichuanInputType"]]


class _TransformFuncDict(TypedDict):
    loader: importlib.machinery.SourceFileLoader
    module: types.ModuleType
    last_m: float


_TransformFunction = Callable[[BaichuanInputType, int, random.Random], BaichuanInputType]


class BaichuanBatch(TypedDict):
    inputs: NDArray[np.int32]
    length: NDArray[np.int32]
    context: NDArray[np.bool_]
    sample_ids: NDArray[np.int32]
    spans: NDArray[np.int32]
    target: NDArray[np.int32]
    task_ids: NDArray[np.int32]
    task_names: List[str]
    raw_data: List[Any]

def build_chat_input(tokenizer, messages: List[dict]):
    def _parse_messages(messages, split_role="user"):
        system, rounds = "", []
        round = []
        for i, message in enumerate(messages):
            if message["role"] == "system":
                assert i == 0
                system = message["content"]
                continue
            if message["role"] == split_role and round:
                rounds.append(round)
                round = []
            round.append(message)
        if round:
            rounds.append(round)
        return system, rounds

    system, rounds = _parse_messages(messages, split_role="user")
    system_tokens = tokenizer.encode(system)

    history_tokens = []
    for round in rounds[::-1]:
        round_tokens = []
        for message in round:
            if message["role"] == "user":
                round_tokens.append(195)
            else:
                round_tokens.append(196)
            round_tokens.extend(tokenizer.encode(message["content"]))
        history_tokens = round_tokens + history_tokens  # concat left

    input_tokens = system_tokens + history_tokens
    if messages[-1]["role"] != "assistant":
        input_tokens.append(196)
    return input_tokens


def convert_data_to_id(tokenizer: BaichuanTokenizer, data: Any):
    input_ids = build_chat_input(tokenizer=tokenizer, messages=data["input"])
    output_ids = tokenizer.encode(data["output"])
    ids = input_ids + output_ids + [tokenizer.eos_token_id]
    ids = np.array(ids, dtype=np.int32)
    context = np.zeros((ids.shape[0],), dtype=np.int8)
    context[: len(input_ids)] = 1
    return ids, context


def _dataset_identity(c: _MixedDatasetConfig):
    return "{}.{}".format(c["task_name"], c["dataset_name"])


class _MixedDatasetBatchPacker:
    def __init__(
        self,
        batch_size: int,
        max_length: int,
        tokenizer: BaichuanTokenizer,
        unpad: bool = False,
    ) -> None:
        self._batch_size = batch_size
        self._max_length = max_length
        self._clip_length = max_length
        self.tokenizer = tokenizer
        self._transform_func_table: Dict[str, _TransformFuncDict] = {}
        self._unpad = unpad
        if unpad:
            self._max_length = max_length * batch_size
            self._batch_size = 1

        self._inputs: List[NDArray[np.int32]] = []
        self._context: List[NDArray[np.int8]] = []
        self._sample_ids: List[NDArray[np.int32]] = []
        self._spans: List[List[int]] = []
        self._task_ids: List[List[str]] = []
        self._raw_data: List[List[Any]] = []

    def __len__(self):
        return len(self._inputs)

    def apply_transform(
        self,
        data: BaichuanInputType,
        transform: Union[Dict[str, Any], Callable[[BaichuanInputType], BaichuanInputType], None],
    ) -> BaichuanInputType:
        if transform is None:
            return data
        if not isinstance(transform, dict):
            return transform(data)  # transform function

        mapping_list: List[Tuple[str, str]] = []

        def _walk_transform_dict(data: Union[Dict[str, Any], str], prefix: str = ""):
            if isinstance(data, dict):
                for k, v in data.items():
                    if len(prefix) > 0:
                        _walk_transform_dict(v, prefix + "." + k)
                    else:
                        _walk_transform_dict(v, k)
            else:
                assert isinstance(data, str), "Invalid transform {}".format(data)
                mapping_list.append((prefix, data))

        _walk_transform_dict(transform)

        expanded_mapping_list: List[Tuple[str, Any]] = []

        def _expand_mapping(data: BaichuanInputType, stars: List[str], path: List[str], target: List[str]):
            if len(path) == 0:
                num_stars = 0
                for it in target:
                    if it == "*":
                        num_stars += 1
                if num_stars != len(stars):
                    raise ValueError("Invalid transform {}".format(".".join(target)))

                nw_tgt = []
                num_stars = 0
                for it in target:
                    if it == "*":
                        nw_tgt.append(stars[num_stars])
                        num_stars += 1
                    else:
                        nw_tgt.append(it)
                expanded_mapping_list.append((".".join(nw_tgt), data))
            else:
                if not isinstance(data, dict):
                    raise ValueError("Invalid data {}".format(data))
                if path[0] == "*":
                    for k, v in data.items():
                        _expand_mapping(v, stars + [k], path[1:], target)
                else:
                    _expand_mapping(data[path[0]], stars, path[1:], target)

        # expand mapping list
        for tgt, src in mapping_list:
            if src.startswith("$"):
                # copy from src
                _expand_mapping(data, [], src[1:].split("."), tgt.split("."))
            else:
                if "*" in tgt:
                    raise ValueError("Constant value is not allowed to have `*` in prefix")
                expanded_mapping_list.append((tgt, src))

        ret = {}
        for tgt, val in expanded_mapping_list:
            tgt = tgt.split(".")
            cur = ret
            while len(tgt) > 1:
                cur = cur[tgt[0]]
                tgt = tgt[1:]
            cur[tgt[0]] = val
        return ret

    def data_to_id(self, data: Any):
        return convert_data_to_id(self.tokenizer, data)

    def _ensure_transform_function(self, module_name: str, transform_script_path: str) -> _TransformFunction:
        module_name = "cpm_live.transforms.{}".format(module_name)
        if transform_script_path not in self._transform_func_table:
            loader = importlib.machinery.SourceFileLoader(module_name, transform_script_path)
            spec = importlib.util.spec_from_loader(loader.name, loader)
            if spec is None:
                raise RuntimeError("spec is none! {}".format(module_name))
            mod = importlib.util.module_from_spec(spec)
            self._transform_func_table[transform_script_path] = {
                "loader": loader,
                "module": mod,
                "last_m": 0,
            }

        transform_script_info = self._transform_func_table[transform_script_path]
        curr_m_time = float(transform_script_info["loader"].path_stats(transform_script_path)["mtime"])
        if curr_m_time > transform_script_info["last_m"]:
            transform_script_info["last_m"] = curr_m_time
            transform_script_info["loader"].exec_module(transform_script_info["module"])
        transform_func = getattr(transform_script_info["module"], "transform", None)
        if transform_func is None:

            def _empty_transform_func(data: BaichuanInputType, num_sample: int, r: random.Random):
                raise NotImplementedError("Transform func for dataset {} not implemented".format(module_name))

            return _empty_transform_func
        else:
            return transform_func

    def build_instance(self, config: _MixedDatasetConfig):
        _sample_weight = np.array(config["incontext_weight"], dtype=np.float32)
        _sample_weight = _sample_weight / _sample_weight.sum()
        num_incontext = np.random.choice(_sample_weight.shape[0], p=_sample_weight)
        ds = config["dataset"]
        transforms = config["transforms"]
        if isinstance(transforms, str):
            if not os.path.exists(transforms):
                raise RuntimeError("transform script {} file not exists".format(transforms))
            # load transform script
            transform_func = self._ensure_transform_function(_dataset_identity(config), transforms)
            seed = random.random()

            def _transform(data: BaichuanInputType):
                r = random.Random(seed)
                return transform_func(data, num_incontext, r)

            transform = _transform
        elif len(transforms) == 0:
            transform = None
        else:
            transform = transforms[np.random.choice(len(transforms))]

        raw_data = {}
        while True:
            inp = ds.read()
            inp = self.apply_transform(inp, transform)
            input_ids, context = self.data_to_id(inp)
            if input_ids.shape[0] > self._clip_length:
                continue  # too long
            input_ids = input_ids[: self._clip_length]
            context = context[: self._clip_length]
            raw_data["input"] = inp
            raw_data["samples"] = []
            break

        sample_ids = np.zeros(input_ids.shape, dtype=np.int32)
        for i in range(num_incontext):
            if input_ids.shape[0] >= self._clip_length:
                break  # early break
            sample = ds.read()
            sample = self.apply_transform(sample, transform)
            sample_input_ids, _ = self.data_to_id(sample)
            if input_ids.shape[0] + sample_input_ids.shape[0] > self._clip_length:
                break  # too long, break
            raw_data["samples"].append(sample)
            input_ids = np.concatenate([input_ids, sample_input_ids], axis=0)
            context = np.concatenate([context, np.ones(sample_input_ids.shape, dtype=np.int8)], axis=0)
            sample_ids = np.concatenate([sample_ids, np.full(sample_input_ids.shape, i + 1, dtype=np.int32)], axis=0)

        return (
            input_ids,
            context,
            sample_ids,
            raw_data,
        )

    def pack_batch(self, force: bool = False, unilm=False) -> BaichuanBatch:
        # pack batch
        if len(self._inputs) < self._batch_size:
            if not force:
                raise RuntimeError("Batch insufficient")
            batch_size = len(self._inputs)
        else:
            batch_size = self._batch_size
        max_length = self._max_length  # self._spans[0][-1] if self._unpad else self._max_length
        inputs = np.zeros((batch_size, max_length), dtype=np.int32)
        context = np.zeros((batch_size, max_length), dtype=np.int8)
        sample_ids = np.zeros((batch_size, max_length), dtype=np.int32)
        tgt = np.full((batch_size, max_length), -100, dtype=np.int32)

        spans = np.zeros((batch_size, max_length), dtype=np.int32)
        length = np.zeros((batch_size,), dtype=np.int32)
        task_ids = np.zeros((batch_size, max_length), dtype=np.int32)
        if self._spans[0][-1] != max_length:
            cu_seqlens = np.array([0] + self._spans[0] + [max_length], dtype=np.int32)
        else:
            cu_seqlens = np.array([0] + self._spans[0], dtype=np.int32)
        max_seqlen = int(np.max(cu_seqlens[1:] - cu_seqlens[:-1]))
        position_ids = np.zeros((batch_size, max_length), dtype=np.int32)

        all_task_names: Set[str] = set()
        for i in range(batch_size):
            for task_name in self._task_ids[i]:
                all_task_names.add(task_name)
        task_names: List[str] = list(all_task_names)
        task_name_to_id = {name: i for i, name in enumerate(task_names)}

        raw_data_list: List[Any] = []
        for i in range(batch_size):
            instance_length = self._inputs[i].shape[0]
            inputs[i, :instance_length] = self._inputs[i]
            sample_ids[i, :instance_length] = self._sample_ids[i]
            if unilm:
                context[i, :instance_length] = self._context[i]

            span_begin = 0
            for span_id, (span_end, task_name) in enumerate(zip(self._spans[i], self._task_ids[i])):
                spans[i, span_begin:span_end] = span_id
                position_ids[i, span_begin:span_end] = np.arange(span_end - span_begin)
                task_ids[i, span_begin:span_end] = task_name_to_id[task_name]
                span_begin = span_end
            length[i] = instance_length
            raw_data_list.extend(self._raw_data[i])

            for j in range(instance_length):
                if j > 1 and self._context[i][j] == 0:
                    if self._inputs[i][j] != self.tokenizer.bos_token_id and self._inputs[i][j - 1] != self.tokenizer.eos_token_id:
                        tgt[i, j - 1] = self._inputs[i][j]

        self._inputs = self._inputs[batch_size:]
        self._context = self._context[batch_size:]
        self._sample_ids = self._sample_ids[batch_size:]
        self._spans = self._spans[batch_size:]
        self._task_ids = self._task_ids[batch_size:]
        self._raw_data = self._raw_data[batch_size:]
        return {
            "inputs": inputs,
            "length": length,
            "context": context > 0,
            "sample_ids": sample_ids,
            "spans": spans,
            "cu_seqlens": cu_seqlens,
            "max_seqlen": max_seqlen,
            "position_ids": position_ids,
            "target": tgt,
            "task_ids": task_ids,
            "task_names": task_names,
            "raw_data": raw_data_list,
        }

    def add_data(self, config: _MixedDatasetConfig) -> Optional[BaichuanBatch]:
        (
            input_ids,
            context,
            sample_ids,
            raw_data,
        ) = self.build_instance(config)

        # add to batch
        best_fit: Union[None, int] = None
        best_fit_space: Union[None, int] = None
        for i in range(len(self._inputs)):
            space = self._max_length - self._inputs[i].shape[0]
            if input_ids.shape[0] <= space:
                if best_fit_space is None:
                    best_fit = i
                    best_fit_space = space
                elif best_fit_space > space:
                    best_fit = i
                    best_fit_space = space
        if best_fit is None:
            # add a new instance
            self._inputs.append(input_ids)
            self._context.append(context)
            self._sample_ids.append(sample_ids)
            self._spans.append([input_ids.shape[0]])
            self._task_ids.append([config["task_name"]])
            self._raw_data.append([raw_data])
        else:
            # add to existing instance
            self._inputs[best_fit] = np.concatenate([self._inputs[best_fit], input_ids], axis=0)
            self._context[best_fit] = np.concatenate([self._context[best_fit], context], axis=0)
            self._sample_ids[best_fit] = np.concatenate([self._sample_ids[best_fit], sample_ids], axis=0)
            self._spans[best_fit].append(self._inputs[best_fit].shape[0])
            self._task_ids[best_fit].append(config["task_name"])
            self._raw_data[best_fit].append(raw_data)

        if len(self._inputs) > self._batch_size:
            return self.pack_batch()
        else:
            return None  # not ready


class _MixedDatasetConfigMananger:
    def __init__(self, config_path: str) -> None:
        self._config_path: str = config_path
        self._config: Union[List[_MixedDatasetConfig], None] = None
        self._last_m = 0

    def changed(self):
        while True:
            try:
                m_time = os.stat(self._config_path).st_mtime
                if m_time > self._last_m:
                    # try to load new config
                    try:
                        self._config = json.load(open(self._config_path, "r", encoding="utf-8"))
                    except Exception:
                        # failed to load config
                        return False
                    # new config loaded
                    self._last_m = m_time
                    return True
                return False
            except Exception:
                print("Error: reading info list! {}".format(self._config_path))
                time.sleep(30)

    def get_config(self) -> List[_MixedDatasetConfig]:
        if self._config is None:
            if not self.changed():
                raise RuntimeError("Failed to load config")
            if self._config is None:
                raise RuntimeError("Failed to load config")
        return self._config


def _mixed_dataset_process(
    config_path: str,
    q_cmd: multiprocessing.Queue,
    q_cmd_out: multiprocessing.Queue,
    q_data: multiprocessing.Queue,
    rank: int,
    world_size: int,
    packer: _MixedDatasetBatchPacker,
    max_repeat_times: int = None,
):
    # ignore SIGINT
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)
    config_base_path = os.path.dirname(os.path.abspath(config_path))

    def _convert_to_abs_path(transform_path: str):
        if transform_path.startswith("/"):
            return transform_path
        else:
            return os.path.join(config_base_path, transform_path)

    def _build_sample_weights(config: List[_MixedDatasetConfig]):
        if len(config) == 0:
            return np.array([], dtype=np.float32)
        weights = [c["weight"] * c["lines"] for c in config]
        weights = np.array(weights, dtype=np.float32)
        sm_weight = weights.sum()
        if sm_weight > 0:
            weights = weights / sm_weight
            return weights
        else:
            raise RuntimeError("Empty datasets")

    cfg_mgr = _MixedDatasetConfigMananger(config_path)
    config = cfg_mgr.get_config()

    for c in config:
        ds = DistributedDataset(
            _convert_to_abs_path(c["path"]),
            rank,
            world_size,
            max_repeat_times=max_repeat_times,
        )

        c["lines"] = ds._nlines
        c["dataset"] = ds
        if "weight" not in c:
            c["weight"] = 1.0
        if "transforms" not in c:
            c["transforms"] = []
        elif isinstance(c["transforms"], str):
            c["transforms"] = _convert_to_abs_path(c["transforms"])
        if "incontext_weight" not in c:
            c["incontext_weight"] = [1.0]

    weights = _build_sample_weights(config)

    should_stop = False
    should_start = False

    while not should_stop:
        # update config first
        if cfg_mgr.changed():
            path_ds_map: Dict[str, _MixedDatasetConfig] = {}
            nw_path_set: Set[str] = set()

            # load new config
            nw_config = cfg_mgr.get_config()

            # build path -> dataset map
            for c in config:
                path_ds_map[_dataset_identity(c)] = c

            # add new datasets
            for c in nw_config:
                if _dataset_identity(c) in path_ds_map:
                    # update values only
                    if "weight" in c:
                        path_ds_map[_dataset_identity(c)]["weight"] = c["weight"]
                    if "transform" in c:
                        if isinstance(c["transforms"], str):
                            path_ds_map[_dataset_identity(c)]["transforms"] = _convert_to_abs_path(c["transforms"])
                        else:
                            path_ds_map[_dataset_identity(c)]["transforms"] = c["transforms"]
                    if "incontext_weight" in c:
                        path_ds_map[_dataset_identity(c)]["incontext_weight"] = c["incontext_weight"]
                else:
                    # new dataset
                    ds = DistributedDataset(
                        _convert_to_abs_path(c["path"]),
                        rank,
                        world_size,
                        max_repeat_times=max_repeat_times,
                    )
                    c["lines"] = ds._nlines
                    c["dataset"] = ds
                    if "weight" not in c:
                        c["weight"] = 1.0
                    if "transforms" not in c:
                        c["transforms"] = []
                    elif isinstance(c["transforms"], str):
                        c["transforms"] = _convert_to_abs_path(c["transforms"])
                    if "incontext_weight" not in c:
                        c["incontext_weight"] = [1.0]
                    path_ds_map[_dataset_identity(c)] = c
                nw_path_set.add(_dataset_identity(c))

            # remove unused datasets
            for c in config:
                if _dataset_identity(c) not in nw_path_set:
                    del path_ds_map[_dataset_identity(c)]

            config: List[_MixedDatasetConfig] = []
            for c in nw_config:
                config.append(path_ds_map[_dataset_identity(c)])
            del path_ds_map
            del nw_path_set
            del nw_config

            weights = _build_sample_weights(config)

        # get cmds
        while True:
            try:
                cmd = q_cmd.get_nowait()
            except Empty:
                break
            if cmd == "stop":
                should_stop = True
                q_cmd_out.put(True)
                break
            elif cmd == "state_dict":
                ret = OrderedDict()
                for c in config:
                    ds_name = _dataset_identity(c)
                    ret[ds_name] = c["dataset"]._state_dict()
                q_cmd_out.put(ret)
            elif cmd == "load_state_dict":
                state_dict = q_cmd.get()
                missing = []
                for c in config:
                    ds_name = _dataset_identity(c)
                    if ds_name in state_dict:
                        c["dataset"].load_state_dict(state_dict[ds_name], strict=False)
                    else:
                        # new dataset
                        missing.append(ds_name)
                q_cmd_out.put(missing)
            elif cmd == "start":
                should_start = True
                q_cmd_out.put(True)
            else:
                raise RuntimeError("Unknown command: {}".format(cmd))

        if should_stop:
            break

        if not should_start:
            # wait for start cmd
            time.sleep(1)
            continue

        if len(config) == 0:
            # no dataset available
            time.sleep(1)
            continue

        if q_data.full():
            # queue full
            time.sleep(1)
            continue

        # sample a dataset
        ds_id: int = 0

        while True:
            ds_id = np.random.choice(weights.shape[0], p=weights)
            if config[ds_id]["dataset"]._nlines != config[ds_id]["lines"]:
                # dataset size changed
                for c in config:
                    c["lines"] = c["dataset"]._nlines
                weights = _build_sample_weights(config)
                continue
            else:
                break

        batch = packer.add_data(config[ds_id])
        if batch is not None:
            # new batch comming
            q_data.put(batch)

    # clean queue
    while True:
        try:
            q_data.get_nowait()
        except Empty:
            break


class MixedDataset:
    def __init__(
        self,
        config_path: str,
        batch_size: int,
        max_length: int,
        tokenizer: BaichuanTokenizer,
        unpad: bool = False,
        max_repeat_times: int = None,
    ) -> None:
        self._q_cmd = multiprocessing.Queue()
        self._q_cmd_out = multiprocessing.Queue()
        self._q_data = multiprocessing.Queue(maxsize=1)
        self._packer = _MixedDatasetBatchPacker(batch_size, max_length, tokenizer, unpad)
        self._p = multiprocessing.Process(
            target=_mixed_dataset_process,
            args=(
                config_path,
                self._q_cmd,
                self._q_cmd_out,
                self._q_data,
                bmt.rank(),
                bmt.world_size(),
                self._packer,
                max_repeat_times,
            ),
        )
        self._p.start()
        self._closed = False

    def close(self):
        if not self._closed:
            self._closed = True
            self._q_cmd.put("stop")
            assert self._q_cmd_out.get(), "Failed to stop process"
            self._p.join()

    @property
    def closed(self):
        return self._closed

    def start(self):
        self._q_cmd.put("start")
        return self._q_cmd_out.get()

    def state_dict(self):
        self._q_cmd.put("state_dict")
        states = self._q_cmd_out.get()
        if not isinstance(states, OrderedDict):
            raise RuntimeError("Invalid state dict {}".format(states))
        if bmt.world_size() == 1:
            for val in states.values():
                val["states"].unsqueeze_(0)
                val["block"].unsqueeze_(0)
            return states

        ret = OrderedDict()
        for k, v in states.items():
            num_unused_block = v["states"].size(0)
            gpu_num_unused_block = torch.tensor([num_unused_block], dtype=torch.long).cuda()
            max_unused_blocks = bmt.distributed.all_reduce(gpu_num_unused_block, op="max").cpu().item()
            if max_unused_blocks == 0:
                max_unused_blocks = 1
            gpu_states = torch.full((max_unused_blocks,), -1, dtype=torch.long).cuda()
            gpu_states[:num_unused_block] = v["states"].cuda()

            gpu_block = v["block"].cuda()
            global_states = bmt.distributed.all_gather(gpu_states).cpu()  # (world_size, max_unused_blocks)
            global_block = bmt.distributed.all_gather(gpu_block).cpu()  # (world_size, 4)
            ret[k] = {"states": global_states, "block": global_block}
        return ret

    def load_state_dict(self, data: OrderedDict, strict: bool = False):
        self._q_cmd.put("load_state_dict")
        self._q_cmd.put(data)
        missing = self._q_cmd_out.get()
        if strict:
            if len(missing) > 0:
                raise RuntimeError("Missing dataset state: {}".format(missing))
        return missing

    def get(self) -> BaichuanBatch:
        ret: BaichuanBatch = self._q_data.get()  # type: ignore
        if not isinstance(ret, dict):
            raise RuntimeError("Invalid data {}".format(ret))
        return ret

    def __iter__(self):
        while True:
            yield self.get()

    def __del__(self):
        if not self.closed:
            try:
                self.close()
            except Exception:
                pass
