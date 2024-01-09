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
import torch.nn.functional as F
from typing_extensions import TypedDict

from ...native_layers import Embedding
from ...native_layers import Encoder
from ...native_layers import RotaryEmbeddingESM
from ...utils import Config
from ...utils import gradient_shrink
from .llama import LlamaConfig


class LlamaInferenceState(TypedDict):
    buffer_context: torch.Tensor
    buffer_sample_ids: torch.Tensor
    buffer: List[Tuple[torch.Tensor, torch.Tensor]]


class LlamaTorch(torch.nn.Module):
    def __init__(self, config: LlamaConfig):
        super().__init__()

        self.encoder = Encoder(
            num_layers=config.num_layers,
            dim_model=config.dim_model,
            dim_ff=config.dim_ff,
            num_heads=config.num_heads,
            num_kv_heads=config.num_kv_heads,
            dim_head=config.dim_head,
            activate_fn=config.activate_fn,
            dtype=config.dtype,
            eps=config.eps,
            dropout_p=config.dropout_p,
            scale=config.scale,
            mask_modules=config.mask_modules,
            use_flash_attn=config.use_flash_attn,
        )

        self.input_embedding = Embedding(
            vocab_size=config.vocab_size,
            embedding_size=config.dim_model,
            scale=config.scale,
            dtype=config.dtype,
            init_std=0.02,
        )

        self.position_bias = RotaryEmbeddingESM(
            dim=config.dim_head, dtype=config.dtype, base=config.base, persistent=False, mixed_precision=True
        )

        self.lm_head = Embedding(
            vocab_size=config.vocab_size,
            embedding_size=config.dim_model,
            scale=config.scale,
            dtype=config.dtype,
            init_std=0.02,
        )
        self.flash_impl = False
        self.use_flash_attn = False
        self.flash_attn_mask_shape = "1d"

    def forward(
        self,
        input: torch.Tensor,  # (batch, seqlen) int32
        length: torch.Tensor = None,  # (batch) int32
        context: torch.Tensor = None,  # (batch, seqlen) bool
        span: torch.Tensor = None,  # (batch, seqlen) int32
        cu_seqlens: torch.Tensor = None,  # (real_batch+2) int32
        max_seqlen: int = None,
        position_ids: torch.Tensor = None,  # (batch, seqlen) int32
    ):
        batch = input.size(0)
        seqlen = input.size(1)
        device = input.device

        if length is not None and length.dim() == 1:
            length = torch.arange(seqlen, device=device)[None, :].repeat(batch, 1) < length[:, None]

        # processing masks and position bias bucket
        if not self.use_flash_attn or (self.flash_attn_mask_shape == "2d" and self.flash_impl == "triton"):
            with torch.no_grad():
                # directional mask
                directional_mask_2d = torch.arange(seqlen, device=device) <= torch.arange(seqlen, device=device).view(
                    -1, 1
                )
                # context mask
                attention_mask = context[:, None, :] | (
                    context[:, :, None].logical_not() & directional_mask_2d.view(1, seqlen, seqlen)
                )
                # span mask
                attention_mask = attention_mask & (span[:, None, :] == span[:, :, None])
                # length mask
                attention_mask = length.view(batch, seqlen, 1) & length.view(batch, 1, seqlen) & attention_mask

        hidden_states = self.input_embedding(input)

        if self.use_flash_attn:
            if self.flash_attn_mask_shape == "1d":
                hidden_states = self.encoder(
                    hidden_states,
                    attention_mask=None,
                    position_bias=self.position_bias,
                    pos_bias_type="rotary",
                    length_mask=length,
                    context_mask=context.to(torch.int16) + 2 * (span.to(torch.int16) + length.to(torch.int16)),
                )
            else:
                if self.flash_impl == "triton":
                    mask = attention_mask.unsqueeze(dim=1).contiguous()
                    attention_mask_bias = torch.zeros_like(mask, device="cuda", dtype=torch.float16)
                    attention_mask_bias[mask == False] -= torch.inf
                else:
                    attention_mask_bias = None
                    assert cu_seqlens is not None, "cu_seqlens are needed in Flash Attention cuda impl"
                hidden_states = self.encoder(
                    hidden_states,
                    attention_mask=None,
                    position_bias=self.position_bias,
                    pos_bias_type="rotary",
                    length_mask=None,
                    context_mask=None,
                    attention_mask_bias=attention_mask_bias,
                    cu_seqlens=cu_seqlens,
                    max_seqlen=max_seqlen,
                    position_ids=position_ids,
                )
        else:
            hidden_states = self.encoder(
                hidden_states, attention_mask=attention_mask, position_bias=self.position_bias, pos_bias_type="rotary"
            )

        logits = self.lm_head.projection(hidden_states)

        return logits, hidden_states

    def inference(
        self,
        input: torch.Tensor,  # (batch, len_q) int32
        length: torch.Tensor,  # (batch) int32
        context: torch.Tensor,  # (batch, seqlen) int16
        span: torch.Tensor,  # (batch, seqlen) int32
        past_key_values: Optional[LlamaInferenceState] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, LlamaInferenceState]:
        batch = input.size(0)
        len_q = input.size(1)
        len_buffer = 0
        if past_key_values is None:
            present_buffer = None
        else:
            present_buffer = past_key_values["buffer"]
            len_buffer = present_buffer[0][0].shape[-2]
        seqlen = len_buffer + len_q
        with torch.no_grad():
            device = input.device
            if length.dim() == 1:
                length = (torch.arange(seqlen, device=device)[None, :].repeat(batch, 1) + length[:, None]) >= seqlen
            directional_mask_2d = torch.arange(seqlen, device=device) <= torch.arange(seqlen, device=device).view(-1, 1)
            # context mask
            attention_mask = context[:, None, :] | (
                context[:, :, None].logical_not() & directional_mask_2d.view(1, seqlen, seqlen)
            )
            # span mask
            attention_mask = attention_mask & (span[:, None, :] == span[:, :, None])
            # length mask
            attention_mask = length.view(batch, seqlen, 1) & length.view(batch, 1, seqlen) & attention_mask

        hidden_states = self.input_embedding(input)

        hidden_states, present_key_values, _ = self.encoder(
            hidden_states,
            attention_mask=attention_mask[:, len_buffer:],
            position_bias=self.position_bias,
            use_cache=True,
            past_key_values=present_buffer,
            pos_bias_type="rotary",
        )

        logits = self.lm_head.projection(hidden_states)

        return (
            logits,
            hidden_states,
            {"buffer": present_key_values},
        )
