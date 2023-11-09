# coding=utf-8
# Copyright 2020 The OpenBMB team. All rights reserved.
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

import json
import math
import os
import random
import shutil
import struct
from queue import Queue
from threading import Thread
from typing import Iterable
from typing import List
from typing import Optional

import torch

from ..utils.log import logger
from .distributed_dataset import _DEFAULT_BLOCK_SIZE
from .distributed_dataset import _random_string
from .distributed_dataset import _read_info_list
from .distributed_dataset import _write_info_list
from .distributed_dataset import build_dataset
from .distributed_dataset import FileInfo
from .distributed_dataset import SimpleDataset
from .serializer import RawSerializer

try:
    from tqdm import tqdm

    support_tqdm = True
except ModuleNotFoundError:
    support_tqdm = False

_DEFAULT_SHUFFLE_BUCKET_SIZE = 1 << 30


def shuffle_dataset(
    path_src: str,
    path_tgt: str,
    block_size: int = _DEFAULT_BLOCK_SIZE,
    bucket_size: int = _DEFAULT_SHUFFLE_BUCKET_SIZE,
    progress_bar: bool = False,
    output_name: Optional[str] = None,
):
    """Shuffle one distributed datataset, write results to another dataset.

    Args:
        path_str (str): path to source dataset
        path_tgt (str): path to write results
        block_size (int): dataset block size (default: 16MB)
        bucket_size (int): shuffle algorithm bucket size (default: 1GB)
        progress_bar (bool): show progress bar

    Example:
        >>> shuffle_dataset("/path/to/source", "/path/to/output")
    """

    if progress_bar and not support_tqdm:
        raise RuntimeError("Requires `tqdm` to enable progress bar.")

    ds = SimpleDataset(path_src, serializer=RawSerializer())
    num_buckets = (ds.nbytes + bucket_size - 1) // bucket_size

    tmp_files = [os.path.join(path_src, ".tmp.%s" % _random_string()) for _ in range(num_buckets)]

    try:
        # Step 1: write to bucket randomly
        f_tmp = [open(fname, "wb") for fname in tmp_files]
        try:
            iterator = ds
            if progress_bar:
                iterator = tqdm(ds, desc="Shuffle step 1/2")
            for data in iterator:
                bucket_id = int(random.random() * num_buckets)
                len_data = len(data)
                f_tmp[bucket_id].write(struct.pack("I", len_data) + data)
        finally:
            # close all files
            for fp in f_tmp:
                if not fp.closed:
                    fp.close()
        f_tmp = []

        # Step 2: shuffle inside bucket
        if output_name is None:
            output_name = "%s.shuffle" % _random_string()
        with build_dataset(
            path_tgt,
            output_name,
            block_size=block_size,
            serializer=RawSerializer(),
        ) as writer:
            iterator = tmp_files
            if progress_bar:
                iterator = tqdm(tmp_files, desc="Shuffle step 2/2")

            for fname in iterator:
                fp = open(fname, "rb")
                data_in_bucket = []
                while True:
                    try:
                        raw_data = fp.read(4)
                        if len(raw_data) == 0:
                            # EOF
                            break
                        len_data = struct.unpack("I", raw_data)[0]
                        data_in_bucket.append(fp.read(len_data))
                    except EOFError:
                        break
                random.shuffle(data_in_bucket)
                for data in data_in_bucket:
                    writer.write(data)
                fp.close()
                os.unlink(fname)
    finally:
        # cleanup
        for fname in tmp_files:
            if os.path.exists(fname):
                os.unlink(fname)


def compact_dataset(path: str):
    """Compact the dataset, removes blocks which the files were deleted.

    **Note** This may affect the existing dataset state dict.

    Args:
        path (str): path to dataset

    Example:
        >>> compact_dataset("/path/to/dataset")

    """

    meta_path = os.path.join(path, "meta.bin")

    info: List[FileInfo] = []
    if os.path.exists(meta_path):
        info = _read_info_list(meta_path)
    else:
        raise ValueError("Dataset not exists")

    nw_info: List[FileInfo] = []
    curr_block = 0
    for v in info:
        if not os.path.exists(v.file_name):
            # file is deleted
            pass
        else:
            num_file_block = v.block_end - v.block_begin
            nw_info.append(
                FileInfo(
                    v.file_name,
                    curr_block,
                    curr_block + num_file_block,
                    v.nbytes,
                    v.nlines,
                    v.mask,
                    v.block_size,
                )
            )
            curr_block += num_file_block

    _write_info_list(meta_path, nw_info)


def mask_dataset(path: str, dbname: str, mask: bool = True):
    """Mask one file in dataset. Blocks in masked datasets won't be read later.

    Args:
        path (str): path to dataset
        dbname (str): file name in this dataset which you want to mask
        mask (bool): True for mask, False for unmask

    Example:
        >>> mask_dataset("/path/to/dataset", "data_part_1", mask=True)

    """

    meta_path = os.path.join(path, "meta.bin")

    info: List[FileInfo] = []
    if os.path.exists(meta_path):
        info = _read_info_list(meta_path)
    else:
        raise ValueError("Dataset not exists")

    for v in info:
        if v.file_name == dbname:
            v.mask = mask
    _write_info_list(meta_path, info)


def merge_dataset(dst: str, src: str):
    meta_path_src = os.path.join(src, "meta.bin")
    meta_path_dst = os.path.join(dst, "meta.bin")

    info_src: List[FileInfo] = []
    if os.path.exists(meta_path_src):
        info_src = _read_info_list(meta_path_src)
    else:
        raise ValueError("Dataset not exists")

    info_dst: List[FileInfo] = []
    if os.path.exists(meta_path_dst):
        info_dst = _read_info_list(meta_path_dst)
    else:
        raise ValueError("Dataset not exists")

    curr_block = 0
    nw_info: List[FileInfo] = []
    for v in info_dst:
        num_file_block = v.block_end - v.block_begin
        nw_info.append(
            FileInfo(
                v.file_name,
                curr_block,
                curr_block + num_file_block,
                v.nbytes,
                v.nlines,
                v.mask,
                v.block_size,
            )
        )
        curr_block += num_file_block

    for v in info_src:
        num_file_block = v.block_end - v.block_begin

        dst_db_name = os.path.join(dst, v.file_name)
        nw_fname = v.file_name
        if os.path.exists(dst_db_name):
            idx = 0
            while os.path.exists(dst_db_name + "_{}".format(idx)):
                idx += 1
            dst_db_name = dst_db_name + "_{}".format(idx)
            nw_fname = nw_fname + "_{}".format(idx)

        shutil.copy(os.path.join(src, v.file_name), dst_db_name)
        nw_info.append(
            FileInfo(
                nw_fname,
                curr_block,
                curr_block + num_file_block,
                v.nbytes,
                v.nlines,
                v.mask,
                v.block_size,
            )
        )
        curr_block += num_file_block

    _write_info_list(meta_path_dst, nw_info)


def to_cpm(src_data, dst_path, dst_name):
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    logger.info(f"src_data: {src_data}")
    logger.info(f"dst_path: {dst_path}")
    logger.info(f"dst_name: {dst_name}")

    tmp_dst_path = dst_path.rstrip("/") + "_tmp"
    if not os.path.exists(tmp_dst_path):
        os.makedirs(tmp_dst_path)

    logger.info(f"write binary into: {tmp_dst_path}")
    with build_dataset(tmp_dst_path, dst_name) as dataset:
        if os.path.isdir(src_data):
            filenames = [os.path.join(src_data, name) for name in os.listdir(src_data)]
        else:
            filenames = [src_data]

        n_filenames = len(filenames)
        for idx, filename in enumerate(filenames):
            logger.info(f"deal: [{n_filenames} -> {idx}] {filename}")
            if not os.path.exists(filename):
                logger.error(f"not exist: {filename}")
                continue

            with open(filename, "r", encoding="utf-8") as fin:
                for line in fin:
                    line = line.strip()
                    dataset.write(json.loads(line))

    logger.info(f"shuffle binary data from {tmp_dst_path} to {dst_path}")
    shuffle_dataset(tmp_dst_path, dst_path, progress_bar=True, output_name=dst_name)

    if os.path.exists(tmp_dst_path):
        shutil.rmtree(tmp_dst_path)


def random_range(start, stop=None, step=None):
    """
    Generator of non-repeated random permutation with the same inteface of python
    `range`. Obtained from https://stackoverflow.com/a/53551417
    The random.shuffle(list) and random.sample(list, len(list)) require
    materialize the lists, which result in a long initalization period.
    """
    if stop is None:
        start, stop = 0, start
    if step is None:
        step = 1
    # Use a mapping to convert a standard range into the desired range.
    mapping = lambda i: (i * step) + start
    # Compute the number of numbers in this range.
    maximum = int(math.ceil((stop - start) / step))
    if maximum == 0:
        # early return with empty range
        yield from ()
        return
    # Seed range with a random integer.
    value = random.randint(0, maximum)
    # Construct an offset, multiplier, and modulus for a linear
    # congruential generator. These generators are cyclic and
    # non-repeating when they maintain the properties:
    #
    #   1) "modulus" and "offset" are relatively prime.
    #   2) ["multiplier" - 1] is divisible by all prime factors of "modulus".
    #   3) ["multiplier" - 1] is divisible by 4 if "modulus" is divisible by 4.

    # Pick a random odd-valued offset.
    offset = random.randint(0, maximum) * 2 + 1
    # Pick a multiplier 1 greater than a multiple of 4.
    multiplier = 4 * (maximum // 4) + 1
    # Pick a modulus just big enough to generate all numbers (power of 2).
    modulus = int(2 ** math.ceil(math.log2(maximum)))
    # Track how many random numbers have been returned.
    found = 0
    while found < maximum:
        # If this is a valid value, yield it in generator fashion.
        if value < maximum:
            found += 1
            yield mapping(value)
        # Calculate the next value in the sequence.
        value = (value * multiplier + offset) % modulus


class Range(object):
    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step

    def __repr__(self):
        return f"Range({self.start}, {self.stop}, {self.step})"

    def iterate(self):
        yield from range(self.start, self.stop, self.step)

    def list(self):
        return list(range(self.start, self.stop, self.step))

    def subrange(self, split, nsplits):
        # strided spliting range params
        # e.g., [0, 3, 5, 7, 9] can be split into [0, 5, 9] and [3, 7]
        return Range(self.start + self.step * split, self.stop, self.step * nsplits)

    def random_iterate(self):
        yield from random_range(self.start, self.stop, self.step)


class CudaPrefetcher(Iterable):
    """
    Wrap around a batch iterator for asynchornously copying data to gpu to shield memcpy latency.
    """

    def __init__(self, loader):
        self.loader = iter(loader)
        self.stream = torch.cuda.Stream()
        self.preload()

    def preload(self):
        try:
            self.data = next(self.loader)
        except StopIteration:
            self.data = None
            return
        with torch.cuda.stream(self.stream):
            for key in self.data.keys():
                if isinstance(self.data[key], torch.Tensor):
                    self.data[key] = self.data[key].cuda(non_blocking=True)

    def __next__(self):
        torch.cuda.current_stream().wait_stream(self.stream)
        data = self.data
        self.preload()
        return data

    def __iter__(self):
        return self


class ThreadedPrefetcher(Thread):
    def __init__(self, iterable, prefetch=10):
        """
        Wrap around a data iterator to shield io latency with a daemon thread.
        """
        super(ThreadedPrefetcher, self).__init__()
        self.queue = Queue(maxsize=prefetch)
        self.iterable = iterable
        self.daemon = True
        self.start()

    def run(self):
        try:
            for data in self.iterable:
                self.queue.put(data)
        except Exception as exception:
            self.queue.put(exception)
        finally:
            self.queue.put(StopIteration())

    def __next__(self):
        item = self.queue.get()
        if isinstance(item, Exception):
            raise item
        else:
            return item

    def __iter__(self):
        return self
