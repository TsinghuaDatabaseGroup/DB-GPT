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

import math

import torch
import torch.nn.functional as F


class Linear(torch.nn.Module):
    def __init__(
        self,
        dim_in: int,
        dim_out: int,
        bias: bool = False,
        dtype: torch.dtype = torch.half,
        init_mean: float = 0.0,
        init_std: float = 1,
        scale: bool = True,
        scale_before: bool = False,
    ):
        super().__init__()
        self.dim_in = self.in_features = dim_in
        self.dim_out = self.out_features = dim_out
        self.scale = scale
        self.scale_before = scale_before
        self.weight = torch.nn.parameter.Parameter(torch.empty((dim_out, dim_in), dtype=dtype))
        torch.nn.init.normal_(self.weight, mean=init_mean, std=init_std)
        self.bias = None
        if bias:
            self.bias = torch.nn.parameter.Parameter(torch.empty(dim_out, dtype=dtype))
            torch.nn.init.normal_(self.bias, mean=init_mean, std=init_std)

    def forward(self, x: torch.Tensor):
        """
        Args:
            x (:obj:`torch.Tensor` of shape ``(batch, seq_len, dim_in)``): The input of linear layer
        Returns:
            :obj:`torch.Tensor` of shape ``(batch, seq_len, dim_out)``: The output of the linear transform y.
        """  # noqa: E501
        if self.scale:
            if self.scale_before:
                x = x / math.sqrt(self.dim_in)
                x = F.linear(x, self.weight, bias=self.bias)
            else:
                x = F.linear(x, self.weight, bias=self.bias)
                x = x / math.sqrt(self.dim_in)
        else:
            x = F.linear(x, self.weight, bias=self.bias)
        return x
