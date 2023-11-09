import torch


def pad(orig_items, key, padding_value=0, padding_side="left"):
    items = []
    if isinstance(orig_items[0][key], list):
        assert isinstance(orig_items[0][key][0], torch.Tensor)
        for it in orig_items:
            for tr in it[key]:
                items.append({key: tr})
    else:
        assert isinstance(orig_items[0][key], torch.Tensor)
        items = orig_items

    batch_size = len(items)
    shape = items[0][key].shape
    dim = len(shape)
    assert dim <= 3
    max_length = max(item[key].shape[-1] for item in items)
    min_length = min(item[key].shape[-1] for item in items)
    dtype = items[0][key].dtype

    if dim == 1:
        return torch.cat([item[key] for item in items], dim=0)
    elif dim == 2:
        if max_length == min_length:
            return torch.cat([item[key] for item in items], dim=0)
        tensor = torch.zeros((batch_size, max_length), dtype=dtype) + padding_value
    else:
        tensor = torch.zeros((batch_size, max_length, shape[-1]), dtype=dtype) + padding_value

    for i, item in enumerate(items):
        if dim == 2:
            if padding_side == "left":
                tensor[i, -len(item[key][0]) :] = item[key][0].clone()
            else:
                tensor[i, : len(item[key][0])] = item[key][0].clone()
        elif dim == 3:
            if padding_side == "left":
                tensor[i, -len(item[key][0]) :, :] = item[key][0].clone()
            else:
                tensor[i, : len(item[key][0]), :] = item[key][0].clone()

    return tensor


def pad_raw(orig_items, max_length=1024, padding_value=0, padding_side="left"):
    max_cols = max(tensor.size(1) for tensor in orig_items)

    padded_arrays = []
    for tensor in orig_items:
        pad_cols = max_cols - tensor.size(1)
        if padding_side == "left":
            padded_tensor = torch.cat([torch.zeros(tensor.size(0), pad_cols), tensor], dim=1)
        elif padding_side == "right":
            padded_tensor = torch.cat([tensor, torch.zeros(tensor.size(0), pad_cols)], dim=1)
        else:
            raise ValueError("Invalid 'side' parameter. Must be 'left' or 'right'.")
        padded_arrays.append(padded_tensor)

    padded_tensor = torch.cat(padded_arrays, dim=0).to(dtype=torch.int32)
    return padded_tensor
