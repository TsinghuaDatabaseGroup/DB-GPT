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

from typing import List
from typing import Optional
from typing import Tuple

import torch

from .blocks import TransformerBlock
from .layernorm import LayerNorm


class Encoder(torch.nn.Module):
    """Layers of encoder transformer blocks plus an final layernorm.

    Args:
        num_layers (int): number of layers.
        dim_model (int): main dimension of modules in transformer blocks.
        dim_ff (int): dim_ff used in :py:class:`model_center.layer.FeedForward`.
        num_heads (int): num_heads used in :py:class:`model_center.layer.Attention`.
        dim_head (int): dim_head used in :py:class:`model_center.layer.Attention`.
        dtype (optional): Defaults to torch.half.
        eps (float, optional): eps used in :py:class:`model_center.layer.LayerNorm`. Defaults to 1e-6.
        dropout_p (float, optional): Defaults to 0.
    """  # noqa: E501

    def __init__(
        self,
        num_layers: int,
        dim_model: int,
        dim_ff: int,
        num_heads: int,
        dim_head: int,
        num_kv_heads: int = -1,
        activate_fn: str = "gelu",
        dtype: torch.dtype = torch.half,
        eps: float = 1e-6,
        dropout_p: Optional[float] = None,
        scale: bool = True,
        add_qkv_bias: bool = False,
        mask_modules: Optional[List[Tuple[bool, bool]]] = None,
        use_flash_attn: bool = False,
    ):
        super().__init__()
        if num_kv_heads == -1:
            num_kv_heads = num_heads
        self.num_layers = num_layers

        if mask_modules is not None:
            assert len(mask_modules) == num_layers, "The total number of masks should equal to num_layers"
            for mask_module in mask_modules:
                assert len(mask_module) == 2, "For encoder, each mask should be (mask_att, mask_ffn)"
        else:
            mask_modules = [(False, False)] * num_layers

        self.layers = torch.nn.ModuleList(
            [
                TransformerBlock(
                    dim_model=dim_model,
                    dim_ff=dim_ff,
                    num_heads=num_heads,
                    num_kv_heads=num_kv_heads,
                    dim_head=dim_head,
                    activate_fn=activate_fn,
                    dtype=dtype,
                    eps=eps,
                    dropout_p=dropout_p,
                    scale=scale,
                    add_qkv_bias=add_qkv_bias,
                    mask_att=mask_modules[ith][0],
                    mask_ffn=mask_modules[ith][1],
                    use_flash_attn=use_flash_attn,
                )
                for ith in range(num_layers)
            ]
        )

        self.output_layernorm = LayerNorm(dim_norm=dim_model, dtype=dtype, eps=eps)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: torch.Tensor = None,
        position_bias: torch.Tensor = None,
        use_cache: bool = False,
        past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        pos_bias_type: Optional[str] = "relative",
        length_mask: Optional[torch.Tensor] = None,
        context_mask: Optional[torch.Tensor] = None,
        attention_mask_bias: Optional[torch.Tensor] = None,
        cu_seqlens: Optional[torch.Tensor] = None,
        max_seqlen: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
    ):
        """
        Args:
            hidden-states (:obj:`torch.Tensor` of shape ``(batch, seq_enc, dim_model)``): Input of encoder, might be the embedding of a batch of sequences.
            attention_mask (:obj:`torch.Tensor` of shape ``(batch, seq_enc, seq_enc)``): Avoid invalid areas to participate in the calculation
            position_bias(:obj:`torch.Tensor` of shape ``(num_heads, seq_enc, seq_enc)``) Provides position information to attention mechanism.

        Return:
            :obj:`torch.Tensor` of shape ``(batch, seq_enc, dim_model)``: The encoder output.

        """  # noqa: E501
        if not use_cache:
            for i, module in enumerate(self.layers):
                hidden_states = module(
                    hidden_states,
                    attention_mask,
                    position_bias,
                    False,
                    None,
                    pos_bias_type,
                    length_mask,
                    context_mask,
                    attention_mask_bias,
                    cu_seqlens,
                    max_seqlen,
                    position_ids,
                )
            hidden_states = self.output_layernorm(hidden_states)
            return hidden_states
        else:
            with torch.no_grad():
                current_key_values = []
                current_hidden_states = []
                for i, module in enumerate(self.layers):
                    hidden_states = module(
                        hidden_states,
                        attention_mask,
                        position_bias,
                        use_cache,
                        past_key_values[i] if past_key_values else None,
                        pos_bias_type,
                        length_mask,
                        context_mask,
                        attention_mask_bias,
                    )
                    if use_cache:
                        current_key_values.append(hidden_states[1])
                        current_hidden_states.append(hidden_states[0])
                        hidden_states = hidden_states[0]
                hidden_states = self.output_layernorm(hidden_states)
                if use_cache:
                    return hidden_states, current_key_values, current_hidden_states
                else:
                    return hidden_states
