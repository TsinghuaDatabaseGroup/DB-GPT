#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @2023 AI, ZHIHU Inc. (zhihu.com)
#
# @author: ouzebin <ouzebin@zhihu.com>
# @date: 2023/07/27
"""
使用 IndexedDataset 前需按指定格式构建或者转换已有数据集
数据集文件结构：
- <dataset name>
    - data.jsonl  # jsonl 格式的数据，每一行一条样本
    - index  # 记录每一行 json 数据的起始 byte-offset

从头构建：直接使用 IndexedDatasetBuilder 这个 context manager
>>>    with IndexedDatasetBuilder("swear", overwrite=True) as builder:
>>>        for data in [{"input": f"screw it {i}", "output": f"for god's sake {i}"} for i in range(100)]:
>>>            builder.put(data)
转换：
从 CPM distributed_dataset 转换：使用 `cpm.dataset.tools.distributed_to_indexed`
$ python -m cpm.dataset.tools.distributed_to_indexed -i <原数据集文件夹> -o <新数据集文件夹>
已有 jsonl 数据：使用 `cpm.dataset.tools.jsonl_to_index` 构建 index 文件。需提前先把 jsonl 文件命名为
$ python -m cpm.dataset.tools.jsonl_to_index -p <数据集文件夹路径>
"""

import itertools
import math
import os
import pickle
import queue
import random
import threading
import time

import bmtrain as bmt

try:
    import msgspec

    json_decode = msgspec.json.decode
    json_encode = msgspec.json.encode
except ModuleNotFoundError:
    import json

    json_decode = json.loads
    json_encode = json.dumps

import torch
from torch.utils.data import Dataset
from typing_extensions import TypedDict

from .utils import Range

print_lock = threading.Lock()


def safe_print(*args, **kargs):
    if "flush" in kargs:
        flush = kargs["flush"]
        del kargs["flush"]
    else:
        flush = True
    with print_lock:
        print(*args, **kargs, flush=flush)


def concurrent_info():
    world_size, rank = bmt.world_size(), bmt.rank()
    worker_info = torch.utils.data.get_worker_info()
    if worker_info is None:
        nworkers, worker_id = 1, 1
    else:
        nworkers, worker_id = worker_info.num_workers, worker_info.id
    return world_size, rank, nworkers, worker_id


class IndexedDataset(Dataset):
    def __init__(self, path, max_retry=1, retry_sleep=5):
        super().__init__()
        self.path = path
        self.max_retry = max_retry
        self.retry_sleep = retry_sleep
        self.bounds = None
        self.build_index()

    def size(self):
        return self.bounds[-1]

    def build_index(self):
        with open(os.path.join(self.path, "index"), "r") as fin:
            self.bounds = [int(line) for line in fin]

    def safe_read(self, i_or_s, offset, size):
        for retry in itertools.count():
            try:
                # destroy the file identifier to avoid pressure on alluxio
                # buffering=0 to avoid overhead during file.seek() and open()
                with open(os.path.join(self.path, "data.jsonl"), "rb", buffering=0) as fin:
                    fin.seek(offset)
                    raw = fin.read(size)
                return raw
            except OSError as e:
                if retry >= self.max_retry:
                    raise OSError(f"reach maximum #retry: {retry}, the file system is broken.")
                safe_print(
                    f"retry loading {self.path}:{i_or_s} in {self.retry_sleep} seconds due to error: '{repr(e)}'"
                )
                time.sleep(self.retry_sleep)
            except ValueError as e:
                # reading error during python io, skip
                safe_print(f"skipping {self.path}:{i_or_s} due to error: '{repr(e)}'")
                return None

    def __repr__(self):
        return (
            f"IndexedDataset(path={self.path}, max_retry={self.max_retry}, retry_sleep={self.retry_sleep}) "
            f"with {len(self)} entries."
        )

    def __len__(self):
        return len(self.bounds) - 1

    def bound_idx(self, key, strict=False):
        # bound index within the standard range: [0, len(self))
        # useful for tracing buggy entries
        if strict and not (-len(self) <= key < len(self)):
            raise IndexError(f"Index {key} out of range for '{self.path}'")
        key = min(max(-len(self), key), len(self))  # bound key within [-len(self), len(self)]
        key = key if key > 0 else key % len(self)  # remap negative id to positive ones
        return key

    def __getitem__(self, key):
        # supports list-like slicing and indexing. strided slicing is not currently supported.
        # ok: self[1], self[-1], self[1:3], self[-10:-5], self[-10:-5:1], self[:5]
        # not ok: self[-10:-5:2], self[:100:3]
        if isinstance(key, slice):
            if not (key.step == 1 or key.step is None):
                raise ValueError(f"slice step should be 1 or None, not {key.step}")
            start = self.bound_idx(0 if key.start is None else key.start)
            stop = max(self.bound_idx(len(self) if key.stop is None else key.stop), start)
            if stop == start:
                # early returning empty slice
                return list()
            offset, size = self.bounds[start], self.bounds[stop] - self.bounds[start]
            raw = self.safe_read(key, offset, size)
            if raw is None:
                return None
            else:
                return [
                    raw[s - offset : e - offset]
                    for s, e in zip(self.bounds[start:stop], self.bounds[start + 1 : stop + 1])
                ]

        elif isinstance(key, int):
            key = self.bound_idx(key, strict=True)
            offset, size = self.bounds[key], self.bounds[key + 1] - self.bounds[key]
            raw = self.safe_read(key, offset, size)
            return raw
        else:
            raise TypeError(f"indices must be integers or slices, not {type(key)}")


class PrefetchDecodeDataset(IndexedDataset):
    # Add prefetched sampled iterator and state_dict tracking upon the simple IndexedDataset
    # Add safe decoding in iterator
    def __init__(self, *args, decode=json_decode, **kargs):
        super().__init__(*args, **kargs)
        self.decode = decode
        self.lock = threading.Lock()
        self.prev_used = set()  # store previously used index in the checkpoint
        self.used = set()  # track locally used index

    def state_dict(self, gathered=True):
        if not self.prev_used and not self.used:
            return {"prev_used": set()}
        if gathered:
            used = torch.tensor(list(self.used)).cuda()
            size = torch.tensor(used.numel()).cuda()
            max_size = bmt.distributed.all_reduce(size, op="max")
            # allgather requires tensors having the same size
            used = torch.cat([used, torch.full((max_size - size,), -100, device=used.device)], dim=-1)
            all_used = bmt.distributed.all_gather(used).unique()
            all_used = set(all_used.tolist())
            if -100 in all_used:
                all_used.remove(-100)  # remove the padding value
            all_used.union(self.prev_used)
            return {"prev_used": all_used}
        else:
            return {"prev_used": self.prev_used.union(self.used)}

    def load_state_dict(self, state):
        with self.lock:
            self.used = state.get("prev_used", set())

    def reset(self):
        with self.lock:
            self.used = set()
            self.prev_used = set()

    def safe_decode(self, i, raw):
        if raw is None:
            return None
        try:
            return self.decode(raw)
        except Exception as e:
            safe_print(f"Skip decoding {self.path}:{i} due to error '{e}', raw bytes:\n{raw}")
            return None

    def __getitem__(self, key):
        raw = super().__getitem__(key)
        if raw is None:
            return None
        # key should be either a slice or an integer as checked in IndexedDataset
        if isinstance(key, slice):
            return [self.safe_decode(i, r) for i, r in zip(range(key.start, key.stop), raw)]
        else:
            return self.safe_decode(key, raw)

    def loader(self, q, lid, keys, stop):
        # concurrent prefetching worker
        try:
            for key in keys:
                if stop.is_set():
                    break
                # key is either a slice or an integer index
                index = range(key.start, key.stop) if isinstance(key, slice) else [key]
                with self.lock:
                    unused = set(index) - self.used - self.prev_used
                if not unused:
                    # skip used slice / item
                    continue
                # read raw data with IndexedDataset.__getitem__, suspend decoding util we really need it
                raw = super().__getitem__(key)
                if raw is None:
                    continue
                # filter used data
                items = [(i, s) for i, s in zip(index, raw if len(index) > 1 else [raw]) if i in unused]
                random.shuffle(items)
                for item in items:
                    q.put(item)
        finally:
            # signaling the end of iteration to the main thread
            q.put(StopIteration(lid))

    def _iterate(self, key_groups, nprefetch=1000):
        # helper function for concurrent prefetching
        q = queue.Queue(maxsize=nprefetch)
        stop = threading.Event()
        alive = set()
        try:
            for lid, keys in enumerate(key_groups):
                loader = threading.Thread(target=self.loader, args=(q, lid, keys, stop), daemon=True)
                loader.start()
                alive.add(lid)
            while True:
                try:
                    item = q.get(block=False)
                except queue.Empty:
                    if not alive:
                        # no alive loader, thus no item will be put in the queue
                        break
                    else:
                        # new item will be put later, wait for a while
                        time.sleep(0.3)
                        continue
                if isinstance(item, StopIteration):
                    alive.remove(item.value)
                    continue
                i, raw = item
                data = self.safe_decode(i, raw)
                if data is None:
                    continue
                self.used.add(i)
                yield data
            # automatically reset states with graceful ends.
            self.reset()
        finally:
            # ask daemon loaders to stop
            stop.set()

    def iterate(self, nthreads=3, prefetch_sample=100):
        world_size, rank, nworkers, worker_id = concurrent_info()
        nloaders = world_size * nworkers * nthreads
        if len(self) < nloaders:
            raise ValueError(
                f"more concurrent loaders ({nloaders}) than data entries ({len(self)}) in '{self.path}', "
                f"please constrain either "
                f"world_size={world_size}, num_workers={nworkers} or num_threads={nthreads}."
            )
        r = Range(0, len(self), 1)
        # split index among multi-gpu workers
        r = r.subrange(split=rank, nsplits=world_size)
        # split index among multi-process dataloader workers
        r = r.subrange(split=worker_id, nsplits=nworkers)
        # split index among multi-threaded loaders
        id_groups = [r.subrange(split=tid, nsplits=nthreads).random_iterate() for tid in range(nthreads)]
        for data in self._iterate(id_groups, nprefetch=prefetch_sample):
            yield data

    def sliced_iterate(self, nthreads=1, prefetch_slice=3, slice_size=1000):
        world_size, rank, nworkers, worker_id = concurrent_info()
        nloaders = world_size * nworkers * nthreads
        if len(self) < nloaders:
            raise ValueError(
                f"more concurrent loaders ({nloaders}) than data entries ({len(self)}) in '{self.path}', "
                f"please constrain either "
                f"world_size={world_size}, num_workers={nworkers} or num_threads={nthreads}."
            )
        nslices = int(math.ceil(len(self) / slice_size))

        if nslices < nloaders:
            safe_print(
                f"fail to distribute {nslices} slices from '{self.path}' to {nloaders} concurrent loaders, "
                f"reduce slice_size from {slice_size} to {len(self) // nloaders}."
            )
            slice_size = len(self) // nloaders

        # we only iteratre through start ids as they uniquely mark each slice
        r = Range(0, len(self), slice_size)
        # split index among multi-gpu workers
        r = r.subrange(split=rank, nsplits=world_size)
        # split index among multi-process dataloader workers
        r = r.subrange(split=worker_id, nsplits=nworkers)
        # split index among multi-threaded loaders
        slice_groups = [
            (slice(s, s + slice_size) for s in r.subrange(tid, nthreads).random_iterate()) for tid in range(nthreads)
        ]
        for data in self._iterate(slice_groups, nprefetch=prefetch_slice * slice_size):
            yield data


class IndexedDatasetBuilder:
    def __init__(self, path, overwrite=False):
        self.path = path
        self.index_path = os.path.join(self.path, "index")
        self.data_path = os.path.join(self.path, "data.jsonl")
        if not overwrite:
            assert not os.path.exists(self.data_path)
            assert not os.path.exists(self.index_path)
        self.fout = None
        self.starts = []
        self.offset = 0

    def __enter__(self):
        os.makedirs(self.path, exist_ok=True)
        self.fout = open(self.data_path, "wb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.starts.append(self.offset)
        with open(self.index_path, "w") as fout:
            for s in self.starts:
                fout.write(f"{s}\n")
        self.fout.close()

    def put(self, data: dict):
        s = json_encode(data) + b"\n"
        self.starts.append(self.offset)
        self.offset += len(s)
        self.fout.write(s)


if __name__ == "__main__":
    with IndexedDatasetBuilder("swear", overwrite=True) as builder:
        for d in [{"input": f"screw it {i}", "output": f"for god's sake {i}"} for i in range(100)]:
            builder.put(d)
    dataset = IndexedDataset("swear")
    for i in range(10):
        print(dataset[random.randint(0, len(dataset) - 1)])
