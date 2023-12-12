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

import inspect
import math

import bmtrain as bmt
import torch
import torch.nn.functional as F


class LinearFunctionForZeroStage3(torch.autograd.Function):
    # Note that both forward and backward are @staticmethods
    @staticmethod
    # bias is an optional argument
    def forward(ctx, input, weight, bias=None):
        ctx.save_for_backward(input, weight, bias)

        if input.dim() == 2 and bias is not None:
            # fused op is marginally faster
            ret = torch.addmm(bias, input, weight.t())
        else:
            output = input.matmul(weight.t())
            if bias is not None:
                output += bias
            ret = output

        return ret

    # This function has only a single output, so it gets only one gradient
    @staticmethod
    def backward(ctx, grad_output):
        # This is a pattern that is very convenient - at the top of backward
        # unpack saved_tensors and initialize all gradients w.r.t. inputs to
        # None. Thanks to the fact that additional trailing Nones are
        # ignored, the return statement is simple even when the function has
        # optional inputs.
        input, weight, bias = ctx.saved_tensors

        grad_input = grad_weight = grad_bias = None

        # print(f"backward shaped grad_output {grad_output.shape}, input {input.shape}, weight {weight.shape} and bias {bias.shape if bias is not None else None}")
        # These needs_input_grad checks are optional and there only to
        # improve efficiency. If you want to make your code simpler, you can
        # skip them. Returning gradients for inputs that don't require it is
        # not an error.
        if ctx.needs_input_grad[0]:
            # print(f"Computing grad input weight {weight.shape} grad_output {grad_output.shape}")
            grad_input = grad_output.matmul(weight)
            # print(f"Computed grad input {grad_input.shape}")
        if ctx.needs_input_grad[1]:
            # print("Computing grad weight")
            dim = grad_output.dim()
            if dim > 2:
                grad_weight = (
                    grad_output.reshape(-1, grad_output.shape[-1]).t().matmul(input.reshape(-1, input.shape[-1]))
                )
            else:
                grad_weight = grad_output.t().matmul(input)
            # print(f"Computed grad weight grad_weight {grad_weight.shape}")
        if bias is not None and ctx.needs_input_grad[2]:
            # print("Computing grad bias")
            grad_bias = grad_output.sum(0)
            # print("Done computing grad bias")
            # print("needs bias")
        # print(f"backward shaped grad_input {grad_input.shape}, grad_weight {grad_weight.shape}, grad_bias {grad_bias.shape if grad_bias is not None else None}")
        return grad_input, grad_weight, grad_bias


class Linear(bmt.DistributedModule):
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

        self.weight = bmt.DistributedParameter(
            torch.empty((dim_out, dim_in), dtype=dtype),
            init_method=bmt.ParameterInitializer(torch.nn.init.normal_, mean=init_mean, std=init_std),
        )
        self.bias = None
        if bias:
            self.bias = bmt.DistributedParameter(
                torch.empty(dim_out, dtype=dtype),
                init_method=bmt.ParameterInitializer(torch.nn.init.normal_, mean=init_mean, std=init_std),
            )

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
                if "checkpointing" in inspect.signature(bmt.init_distributed).parameters:
                    x = LinearFunctionForZeroStage3.apply(x, self.weight, bias=self.bias)
                else:
                    x = F.linear(x, self.weight, bias=self.bias)
            else:
                if "checkpointing" in inspect.signature(bmt.init_distributed).parameters:
                    x = LinearFunctionForZeroStage3.apply(x, self.weight, bias=self.bias)
                else:
                    x = F.linear(x, self.weight, bias=self.bias)
                x = x / math.sqrt(self.dim_in)
        else:
            if "checkpointing" in inspect.signature(bmt.init_distributed).parameters:
                x = LinearFunctionForZeroStage3.apply(x, self.weight, bias=self.bias)
            else:
                x = F.linear(x, self.weight, bias=self.bias)
        return x
