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
from typing import Optional
from typing import Tuple

try:
    from .flash_triton import FlashAttnFunc
except:
    FlashAttnFunc = None
import bmtrain as bmt
import torch

from .linear import Linear
from .position_embedding import apply_chatglm_rotary_pos_emb

try:
    from flash_attn.flash_attn_interface import flash_attn_unpadded_func
except:
    flash_attn_unpadded_func = None
try:
    from flash_attn.flash_attn_interface import flash_attn_varlen_func
except:
    flash_attn_varlen_func = None

try:
    from flash_attn.bert_padding import pad_input
    from flash_attn.bert_padding import unpad_input
except:
    pad_input = None
    unpad_input = None


class FlashSelfAttention(torch.nn.Module):
    """Implement the scaled dot product attention with softmax.
    Arguments
    ---------
        softmax_scale: The temperature to use for the softmax attention.
                      (default: 1/sqrt(d_keys) where d_keys is computed at
                      runtime)
        attention_dropout: The dropout rate to apply to the attention
                           (default: 0.0)
    """

    def __init__(self, causal=False, softmax_scale=None, attention_dropout=0.0, device=None, dtype=None):
        super().__init__()
        assert flash_attn_unpadded_func is not None, (
            "Please install FlashAttention first, " "e.g., with pip install flash-attn"
        )
        assert rearrange is not None, "Please install einops first, e.g., with pip install einops"
        self.causal = causal
        self.softmax_scale = softmax_scale
        self.dropout_p = attention_dropout

    def forward(self, q, k, v, attention_mask=None, length_mask=None, context_mask=None):
        """Implements the multihead softmax attention.
        Arguments
        ---------
            q, k, v: The tensor containing the query, key, and value. (B, S, H, D)
        """
        assert q.dtype in [torch.float16, torch.bfloat16], q.dtype
        assert q.is_cuda
        batch_size, seqlen = q.shape[0], q.shape[1]
        d = q.shape[-1]

        if length_mask is not None:
            q, k, v = [rearrange(x, "b s h d -> b s (h d)") for x in [q, k, v]]
            q, indices_q, cu_seqlens, max_s = unpad_input(q, length_mask)
            k, _, _, _ = unpad_input(k, length_mask)
            v, _, _, _ = unpad_input(v, length_mask)
            q, k, v = [rearrange(x, "nnz (h d) -> nnz h d", d=d) for x in [q, k, v]]
            output = flash_attn_unpadded_func(
                q,
                k,
                v,
                cu_seqlens,
                cu_seqlens,
                max_s,
                max_s,
                self.dropout_p if self.training else 0.0,
                softmax_scale=self.softmax_scale,
                causal=self.causal,
                attention_mask=attention_mask,
                context_mask=context_mask[:, :max_s],
            )
            # TODO reimplement (un)pad_input to remove redundant rearranges.
            output = rearrange(output, "nnz h d -> nnz (h d)")
            output = pad_input(output, indices_q, batch_size, seqlen)
            output = rearrange(output, "b s (h d) -> b s h d", d=d)
        else:
            q, k, v = [rearrange(x, "b s ... -> (b s) ...") for x in [q, k, v]]
            max_s = seqlen
            cu_seqlens = torch.arange(0, (batch_size + 1) * seqlen, step=seqlen, dtype=torch.int32, device=q.device)

            output = flash_attn_unpadded_func(
                q,
                k,
                v,
                cu_seqlens,
                cu_seqlens,
                max_s,
                max_s,
                self.dropout_p if self.training else 0.0,
                softmax_scale=self.softmax_scale,
                causal=self.causal,
                attention_mask=attention_mask,
                context_mask=context_mask,
            )
            output = rearrange(output, "(b s) ... -> b s ...", b=batch_size)
        return output


class Attention(torch.nn.Module):
    def __init__(
        self,
        dim_model: int,
        num_heads: int,
        num_kv_heads: int,
        dim_head: int,
        dtype: torch.dtype = torch.half,
        dropout_p: Optional[float] = None,
        scale: bool = True,
        add_qkv_bias: bool = False,
        use_flash_attn: bool = False,
    ) -> None:
        super().__init__()

        self.dim_model = dim_model
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads
        self.head_groups = num_heads // num_kv_heads
        self.dim_head = dim_head

        self.project_q = Linear(
            self.dim_model, self.num_heads * self.dim_head, bias=add_qkv_bias, dtype=dtype, scale=scale
        )
        self.project_k = Linear(
            self.dim_model, self.num_kv_heads * self.dim_head, bias=add_qkv_bias, dtype=dtype, scale=scale
        )
        self.project_v = Linear(
            self.dim_model, self.num_kv_heads * self.dim_head, bias=add_qkv_bias, dtype=dtype, scale=scale
        )

        self.attention_out = Linear(self.num_heads * self.dim_head, self.dim_model, dtype=dtype, scale=scale)

        self.softmax = torch.nn.Softmax(dim=-1)

        if dropout_p is not None:
            self.dropout = torch.nn.Dropout(p=dropout_p)
            self.dropout_p = dropout_p
        else:
            self.dropout = None

        # if use_flash_attn:
        #     self.core_attention_flash = FlashSelfAttention(causal=False, attention_dropout=0.0)
        self.use_flash_attn = use_flash_attn

    def forward(
        self,
        hidden_q: torch.Tensor,
        hidden_kv: torch.Tensor,
        attention_mask: torch.BoolTensor,
        position_bias: torch.Tensor,
        use_cache: bool = False,
        past_kv: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        pos_bias_type: Optional[str] = "relative",
        length_mask: Optional[torch.Tensor] = None,
        context_mask: Optional[torch.Tensor] = None,
        attention_mask_bias: Optional[torch.Tensor] = None,
        cu_seqlens: Optional[torch.Tensor] = None,
        max_seqlen: int = None,
        position_ids: Optional[torch.Tensor] = None,
    ):
        """
        Args:
            hidden_q (:obj:`torch.Tensor` of shape ``(batch, len_q, dim_model)``): Indices of input sequence tokens. It will be embedded by model's internal embedding lookup matrix.
            hidden_kv (:obj:`torch.Tensor` of shape ``(batch, len_k, dim_model)``): Length of input sequence before padding.
            attention_mask (:obj:`torch.Tensor` of shape ``(batch, len_q, len_k)``): Used to avoid performing attention on padding token indices.
            position_bias(:obj:`torch.Tensor` of shape ``(num_heads, len_q, len_k)`` or ``(1, num_heads, len_k, len_q)``): Provide positional information about tensor `key_value` and `query`.
        Return:
            out (:obj:`torch.Tensor` of shape ``(batch, len_q, dim_model)``): The attention output.
        """  # noqa: E501

        batch_size = hidden_q.size(0)
        len_q = hidden_q.size(1)
        len_k = hidden_kv.size(1)

        h_q = self.project_q(hidden_q)
        h_k = self.project_k(hidden_kv)
        h_v = self.project_v(hidden_kv)

        if not self.use_flash_attn:
            h_q = h_q / math.sqrt(math.sqrt(self.dim_head))
            h_k = h_k / math.sqrt(math.sqrt(self.dim_head))

            h_q = h_q.view(batch_size, len_q, self.num_heads, self.dim_head).permute(0, 2, 1, 3)
            h_k = h_k.view(batch_size, len_k, self.num_kv_heads, self.dim_head).permute(0, 2, 1, 3)
            h_v = h_v.view(batch_size, len_k, self.num_kv_heads, self.dim_head).permute(0, 2, 1, 3)

        if pos_bias_type == "rotary":
            # b h s d
            h_q, h_k = position_bias(h_q, h_k, -2, offset=past_kv[0].size(-2) if past_kv is not None else 0)
        elif pos_bias_type == "chatglm_rotary":
            h_q = apply_chatglm_rotary_pos_emb(h_q, position_bias)
            h_k = apply_chatglm_rotary_pos_emb(h_k, position_bias)

        if past_kv is not None:
            h_k = torch.cat([past_kv[0], h_k], dim=-2)
            h_v = torch.cat([past_kv[1], h_v], dim=-2)
            len_k = h_k.size(-2)
        # (b, n_h, len_q, d_h) @ (b, n_h, d_h, len_k) -> (b, n_h, len_q, len_k)
        if self.head_groups == 1:
            score = torch.matmul(h_q, h_k.transpose(-1, -2))  # / math.sqrt(self.dim_head) moved to line 75~76
        else:
            score = torch.matmul(
                h_q.reshape(batch_size, self.num_kv_heads, self.head_groups * len_q, self.dim_head),
                h_k.transpose(-1, -2),
            ).view(batch_size, self.num_heads, len_q, len_k)

        if pos_bias_type == "relative":
            if len_q == 1:  # inference with cache
                if len(position_bias.size()) == 4:
                    position_bias = position_bias[:, :, -1:, :]
                else:
                    position_bias = position_bias[:, -1:, :]
            score = score + position_bias
        score = torch.masked_fill(
            score,
            attention_mask.view(batch_size, 1, len_q, len_k) == False,
            torch.scalar_tensor(float("-inf"), device=score.device, dtype=score.dtype),
        )

        score = self.softmax(score)

        score = torch.masked_fill(
            score,
            attention_mask.view(batch_size, 1, len_q, len_k) == False,
            torch.scalar_tensor(0, device=score.device, dtype=score.dtype),
        )

        if self.dropout is not None:
            score = self.dropout(score)

        # (b, n_kv_h, n_h_groups*len_q, len_k) @ (b, n_kv_h, len_k, d_h) -> (b, n_kv_h, n_h_groups*len_q, d_h) -> (b, n_h, len_q, d_h)
        score = torch.matmul(score.view(batch_size, self.num_kv_heads, self.head_groups * len_q, len_k), h_v).view(
            batch_size, self.num_heads, len_q, self.dim_head
        )

        score = score.view(batch_size, self.num_heads, len_q, self.dim_head).permute(0, 2, 1, 3)
        score = score.contiguous().view(batch_size, len_q, self.num_heads * self.dim_head)

        score = self.attention_out(score)

        if use_cache:
            return score, (h_k, h_v)
        else:
            return score
