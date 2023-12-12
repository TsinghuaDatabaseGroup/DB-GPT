#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @2023 AI, ZHIHU Inc. (zhihu.com)
#
# @author: hsd9026 <shengdinghu@gmail.com>
# @date: 2023/07/07
#


import copy

from .log import logger


def num_parameters(model):
    """Return the number of parameters of a model"""
    total_params = 0
    for param_name, param in model.state_dict().items():
        # print(param_name, param.numel())
        total_params += param.numel()
    return total_params


def estimate_parameters(config):
    """Estimate the number of parameters of a model given its config, should be equal to `num_parameters(model)`"""
    # embedding parameters
    embedding_params = config.vocab_size * config.dim_model
    self_attn_params = 4 * config.dim_model * config.dim_head * config.num_heads * config.num_layers
    ff_params = 3 * config.dim_model * config.dim_ff * config.num_layers
    layernorm_parameters = 2 * config.dim_model * config.num_layers
    output_layernorm_parameters = config.dim_model
    positional_bias = 32
    total_params = (
        embedding_params
        + self_attn_params
        + ff_params
        + layernorm_parameters
        + output_layernorm_parameters
        + positional_bias
    )

    params_without_embeddings = total_params - embedding_params

    return total_params, params_without_embeddings


def get_flops_per_token(config):
    """An estimated version of pfdays per token, i.e., the 6N in equation: Computation = 6 N * D."""

    _, N = estimate_parameters(config)

    logger.info(">>>>>> pfdays_per_token >>>> {:,.0f}".format(N))

    # evaluating a forward pass
    C_forward = 6 * N  # + 2 * n_layer * n_ctx * d_model
    # unit = 10**15 * 3600 * 24

    # C_forward = C_forward / unit

    return C_forward
