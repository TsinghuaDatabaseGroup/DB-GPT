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
from typing import Tuple
from typing import Union

import torch
import torch.nn.functional as F


class SegmentPositionEmbedding(torch.nn.Module):
    def __init__(
        self,
        num_heads: int,
        num_segments: int = 1,
        num_buckets: int = 32,
        max_distance: int = 128,
        bidirectional: bool = False,
        dtype: torch.dtype = torch.half,
        init_mean: float = 0.0,
        init_std: float = 1,
    ):
        super().__init__()

        self.num_heads = num_heads
        self.num_buckets = num_buckets
        self.max_distance = max_distance
        self.bidirectional = bidirectional
        self.num_segments = num_segments

        self.relative_attention_bias = torch.nn.parameter.Parameter(
            torch.empty(num_segments * num_segments + num_buckets, num_heads, dtype=dtype)
        )
        torch.nn.init.normal_(self.relative_attention_bias, mean=init_mean, std=init_std)

    def forward(
        self,
        key_pos: torch.Tensor,
        query_pos: torch.Tensor,
        key_segment: torch.Tensor,
        query_segment: torch.Tensor,
    ):
        with torch.no_grad():
            batch = key_pos.size(0)
            keylen = key_pos.size(1)
            querylen = query_pos.size(1)

            assert key_pos.size(0) == query_pos.size(0)
            assert keylen == key_segment.size(1) and querylen == query_segment.size(1)

            key_pos = key_pos.view(batch, -1, keylen)
            query_pos = query_pos.view(batch, querylen, -1)
            key_segment = key_segment.view(batch, -1, keylen)
            query_segment = query_segment.view(batch, querylen, -1)

            relative_position_bucket = self._segment_relative_position_bucket(query_segment, key_segment)
            relative_position_bucket = relative_position_bucket + self.num_buckets  # 与相对位置编码区间不重叠

            # b*q*k
            absolute_position_bucket = self._position_bucket(
                torch.arange(keylen, dtype=torch.int32, device=relative_position_bucket.device)[None, :]
                - torch.arange(querylen, dtype=torch.int32, device=relative_position_bucket.device)[:, None],
                bidirectional=self.bidirectional,
                num_buckets=self.num_buckets,
                max_distance=self.max_distance,
            )
            relative_position_bucket = torch.where(
                (key_segment == query_segment),
                absolute_position_bucket[None, :, :],
                relative_position_bucket,
            )
            # (batch, len_q, len_k)

        # (batch, len_q, len_k, num_heads)
        embeds = F.embedding(relative_position_bucket, self.relative_attention_bias)
        # (batch, num_heads, len_q, len_k)
        embeds = embeds.permute(0, 3, 1, 2).contiguous()
        return embeds

    def _segment_relative_position_bucket(self, query_segment, key_segment):
        return query_segment * self.num_segments + key_segment

    def _position_bucket(self, relative_position, bidirectional=True, num_buckets=32, max_distance=128):
        relative_buckets = 0
        if bidirectional:
            num_buckets //= 2
            relative_buckets = (relative_position > 0).to(torch.int32) * num_buckets
            relative_position = torch.abs(relative_position)
        else:
            relative_position = -torch.min(relative_position, torch.zeros_like(relative_position))
        max_exact = num_buckets // 2
        is_small = relative_position < max_exact
        relative_postion_if_large = max_exact + (
            torch.log(relative_position.float() / max_exact)
            / math.log(max_distance / max_exact)
            * (num_buckets - max_exact)
        ).to(torch.int32)
        relative_postion_if_large = torch.min(
            relative_postion_if_large,
            torch.full_like(relative_postion_if_large, num_buckets - 1),
        )
        relative_buckets += torch.where(is_small, relative_position.to(torch.int32), relative_postion_if_large)
        return relative_buckets


class BucketPositionBias(torch.nn.Module):
    def __init__(
        self,
        num_heads: int,
        num_buckets: int = 32,
        num_segment_bucket: int = 32,
        max_distance: int = 128,
        dtype: torch.dtype = torch.half,
        init_mean: float = 0.0,
        init_std: float = 1,
    ) -> None:
        super().__init__()

        self.num_heads = num_heads
        self.num_buckets = num_buckets
        self.num_segment_bucket = num_segment_bucket
        self.max_distance = max_distance

        self.relative_attention_bias = torch.nn.parameter.Parameter(
            torch.empty(num_buckets + num_segment_bucket, num_heads, dtype=dtype)
        )
        torch.nn.init.normal_(self.relative_attention_bias, mean=init_mean, std=init_std)

    def forward(
        self,
        query_pos: torch.Tensor,  # (batch, len_q)
        key_pos: torch.Tensor,  # (batch, len_k)
        rel_buckets: torch.Tensor,  # (batch, len_q, len_k)
    ):
        with torch.no_grad():
            batch = key_pos.size(0)
            keylen = key_pos.size(1)
            querylen = query_pos.size(1)

            assert key_pos.size(0) == query_pos.size(0)
            assert rel_buckets.size(0) == batch and rel_buckets.size(1) == querylen and rel_buckets.size(2) == keylen

            relative_position_bucket = rel_buckets - 1 + self.num_buckets  # 与相对位置编码区间不重叠

            # b*q*k
            inner_segment_bucket = self._position_bucket(
                key_pos[..., None, :] - query_pos[..., :, None],
                num_buckets=self.num_buckets,
                max_distance=self.max_distance,
            )
            relative_position_bucket = torch.where(
                rel_buckets == 0,
                inner_segment_bucket,
                relative_position_bucket,
            )
            # (batch, len_q, len_k)

        # (batch, len_q, len_k, num_heads)
        embeds = F.embedding(relative_position_bucket, self.relative_attention_bias)
        # (batch, num_heads, len_q, len_k)
        embeds = embeds.permute(0, 3, 1, 2).contiguous()
        return embeds

    def _position_bucket(self, relative_position, num_buckets=32, max_distance=128):
        relative_buckets = 0
        num_buckets //= 2
        relative_buckets = (relative_position > 0).to(torch.int32) * num_buckets
        relative_position = torch.abs(relative_position)

        max_exact = num_buckets // 2
        is_small = relative_position < max_exact
        relative_postion_if_large = max_exact + (
            torch.log(relative_position.float() / max_exact)
            / math.log(max_distance / max_exact)
            * (num_buckets - max_exact)
        ).to(torch.int32)
        relative_postion_if_large = torch.min(
            relative_postion_if_large,
            torch.full_like(relative_postion_if_large, num_buckets - 1),
        )
        relative_buckets += torch.where(is_small, relative_position.to(torch.int32), relative_postion_if_large)
        return relative_buckets


class RotaryEmbedding(torch.nn.Module):
    def __init__(
        self,
        dim,
        base=10000,
        distance_scale: Union[int, float] = 1,
        dtype: torch.dtype = torch.half,
    ):
        super().__init__()
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2, device="cuda", dtype=torch.float32) / dim))
        inv_freq = inv_freq.to(dtype)
        self.distance_scale = distance_scale
        self.dtype = dtype
        self.inv_freq = inv_freq

    def forward(self, x: torch.Tensor, x_pos: torch.Tensor):
        """
        Args:
            x (:obj:`torch.Tensor` of shape ``(..., dim)``): Inputs.
            x_pos (:obj:`torch.Tensor` of shape ``(...)``): Positions of inputs.
        """
        x_pos = x_pos * self.distance_scale
        freqs = x_pos[..., None].to(self.dtype) * self.inv_freq[None, :]  # (..., dim/2)

        # the same implementation as sat
        emb = torch.cat((freqs, freqs), dim=-1)  # (..., dim)
        emb_cos = emb.cos()  # (..., dim)
        emb_sin = emb.sin()  # (..., dim)

        rotate_x = torch.cat([-x[..., x.size(-1) // 2 :], x[..., : x.size(-1) // 2]], dim=-1)  # (..., dim)

        return x * emb_cos + rotate_x * emb_sin


def rotate_half(x):
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(x, cos, sin, seq_dim, offset):
    if x.size(seq_dim) < cos.size(seq_dim):
        cos = cos.narrow(seq_dim, offset, x.size(seq_dim))
        sin = sin.narrow(seq_dim, offset, x.size(seq_dim))
    return (x * cos) + (rotate_half(x) * sin)


def unpad_apply_rotary_pos_emb(x, cos, sin, seq_dim, position_ids):
    cos = cos.index_select(seq_dim, position_ids.squeeze(0))
    sin = sin.index_select(seq_dim, position_ids.squeeze(0))
    return (x * cos) + (rotate_half(x) * sin)


class RotaryEmbeddingESM(torch.nn.Module):
    """
    Rotary position embeddings based on those in
    [RoFormer](https://huggingface.co/docs/transformers/model_doc/roformer). Query and keys are transformed by rotation
    matrices which depend on their relative positions.
    """

    def __init__(
        self,
        dim: int,
        base: Union[int, float] = 10000,
        distance_scale: Union[int, float] = 1,
        dtype=torch.half,
        persistent=True,
        mixed_precision=True,
    ):
        super().__init__()
        self.base = base
        self.distance_scale = distance_scale
        self.dtype = dtype

        # Generate and save the inverse frequency buffer (non trainable)
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2, device="cuda", dtype=torch.float32) / dim))
        if mixed_precision:
            self.register_buffer("inv_freq", inv_freq, persistent=persistent)
        else:
            self.register_buffer("inv_freq", inv_freq.to(self.dtype), persistent=persistent)

        self._seq_len_cached = -1
        self._cos_cached = None
        self._sin_cached = None
        self.mixed_precision = mixed_precision

        self.apply_rotary_pos_emb = apply_rotary_pos_emb
        self.unpad_apply_rotary_pos_emb = unpad_apply_rotary_pos_emb

    def _update_cos_sin_tables(self, x, seq_dim, offset):
        seq_len = x.size(seq_dim) + offset
        if seq_len > self._seq_len_cached or self._cos_cached.device != x.device:
            self._seq_len_cached = seq_len
            t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
            freqs = torch.outer(t * self.distance_scale, self.inv_freq)
            emb = torch.cat((freqs, freqs), dim=-1)
            for i in range(x.dim() - 1):
                if i != seq_dim:
                    emb = emb.unsqueeze_(i)
            if self.mixed_precision:
                self._cos_cached = emb.cos().to(self.dtype)
                self._sin_cached = emb.sin().to(self.dtype)
            else:
                self._cos_cached = emb.cos()
                self._sin_cached = emb.sin()
        return self._cos_cached, self._sin_cached

    def forward(
        self, q: torch.Tensor, k: torch.Tensor, seq_dim, offset=0, cu_seqlens=None, max_length=None, position_ids=None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        seq_dim = (seq_dim + k.dim()) % k.dim()
        self._cos_cached, self._sin_cached = self._update_cos_sin_tables(k, seq_dim, offset)
        return (
            self.apply_rotary_pos_emb(q, self._cos_cached, self._sin_cached, seq_dim, offset),
            self.apply_rotary_pos_emb(k, self._cos_cached, self._sin_cached, seq_dim, offset),
        )


@torch.jit.script
def apply_chatglm_rotary_pos_emb(x: torch.Tensor, rope_cache: torch.Tensor) -> torch.Tensor:
    # x: [b, np, sq, hn]
    x = x.permute(2, 0, 1, 3)  # [b, np, sq, hn] -> [sq, b, np, hn]
    sq, b, np, hn = x.shape
    rot_dim = rope_cache.shape[-2] * 2
    x, x_pass = x[..., :rot_dim], x[..., rot_dim:]
    # truncate to support variable sizes
    rope_cache = rope_cache[:sq]
    xshaped = x.reshape(sq, -1, np, rot_dim // 2, 2)
    rope_cache = rope_cache.view(sq, -1, 1, xshaped.size(3), 2)
    x_out2 = torch.stack(
        [
            xshaped[..., 0] * rope_cache[..., 0] - xshaped[..., 1] * rope_cache[..., 1],
            xshaped[..., 1] * rope_cache[..., 0] + xshaped[..., 0] * rope_cache[..., 1],
        ],
        -1,
    )
    x_out2 = x_out2.flatten(3)
    ret = torch.cat((x_out2, x_pass), dim=-1)
    ret = ret.permute(1, 2, 0, 3)  # [sq, b, np, hn] -> [b, np, sq, hn]
    return ret


class ChatGLMRotaryEmbedding(torch.nn.Module):
    def __init__(self, dim, device="cuda", dtype=torch.float16, persistent=True):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2, dtype=dtype, device=device) / dim))
        self.register_buffer("inv_freq", inv_freq, persistent=persistent)
        self.dim = dim

    def forward_impl(self, seq_len: int, n_elem: int, dtype: torch.dtype, device: torch.device, base: int = 10000):
        """Enhanced Transformer with Rotary Position Embedding.

        Derived from: https://github.com/labmlai/annotated_deep_learning_paper_implementations/blob/master/labml_nn/
        transformers/rope/__init__.py. MIT License:
        https://github.com/labmlai/annotated_deep_learning_paper_implementations/blob/master/license.
        """
        # $\Theta = {\theta_i = 10000^{\frac{2(i-1)}{d}}, i \in [1, 2, ..., \frac{d}{2}]}$
        theta = 1.0 / (base ** (torch.arange(0, n_elem, 2, dtype=dtype, device=device) / n_elem))

        # Create position indexes `[0, 1, ..., seq_len - 1]`
        seq_idx = torch.arange(seq_len, dtype=dtype, device=device)

        # Calculate the product of position index and $\theta_i$
        idx_theta = torch.outer(seq_idx, theta).float()

        cache = torch.stack([torch.cos(idx_theta), torch.sin(idx_theta)], dim=-1)

        # this is to mimic the behaviour of complex32, else we will get different results
        if dtype in (torch.float16, torch.bfloat16, torch.int8):
            cache = cache.bfloat16() if dtype == torch.bfloat16 else cache.half()
        return cache

    def forward(self, max_seq_len, offset: int = 0):
        return self.forward_impl(max_seq_len, self.dim, dtype=self.inv_freq.dtype, device=self.inv_freq.device)
