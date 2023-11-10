#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @2022 AI, ZHIHU Inc. (zhihu.com)
#
# @author: wangchongyi <wangchongyi@zhihu.com>
# @date: 2023/2/28
#
import itertools
import os
import random
from typing import List

import bmtrain as bmt
import torch


class ListDataset(torch.utils.data.Dataset):
    """
    同时支持 map-style 和 iterable-style
    """

    def __init__(
        self, data_list: List, distributed: bool = False, shuffle: bool = True, infinite: bool = False
    ) -> None:
        super(ListDataset, self).__init__()
        if distributed:
            rank = bmt.rank()
            world_size = bmt.world_size()
            self.data_list = list(itertools.islice(data_list, rank, None, world_size))
        else:
            self.data_list = data_list
        self.shuffle = shuffle
        self.infinite = infinite
        self.idx = 0

        if shuffle:
            self._shuffle()

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx >= len(self):
            if self.infinite:
                if self.shuffle:
                    self._shuffle()
                self.idx = 0
            else:
                raise StopIteration
        data = self.data_list[self.idx]
        self.idx += 1
        return data

    def __getitem__(self, idx):
        return self.data_list[idx]

    def __len__(self):
        return len(self.data_list)

    def _shuffle(self):
        random.shuffle(self.data_list)

    def read(self):
        return self.__next__()
