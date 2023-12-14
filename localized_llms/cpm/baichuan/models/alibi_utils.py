import math

import torch


def _get_interleave(n):
    def _get_interleave_power_of_2(nn):
        start = 2 ** (-(2 ** -(math.log2(nn) - 3)))
        ratio = start
        return [start * ratio**i for i in range(nn)]

    if math.log2(n).is_integer():
        return _get_interleave_power_of_2(n)
    else:
        closest_power_of_2 = 2 ** math.floor(math.log2(n))
        return (
            _get_interleave_power_of_2(closest_power_of_2)
            + _get_interleave(2 * closest_power_of_2)[0::2][: n - closest_power_of_2]
        )


def _fill_with_neg_inf(t):
    """FP16-compatible function that fills a tensor with -inf."""
    return t.float().fill_(float("-inf")).type_as(t)


def _buffered_future_mask(seq_len, alibi, num_heads, device, dtype=torch.half):
    """used in training only"""
    _future_mask = torch.triu(_fill_with_neg_inf(torch.zeros([seq_len, seq_len])), 1)
    _future_mask = _future_mask.unsqueeze(0) + alibi
    _future_mask = _future_mask.to(device=device, dtype=dtype)
    assert alibi.shape[0] == num_heads
    return _future_mask[:num_heads, :seq_len, :seq_len]
