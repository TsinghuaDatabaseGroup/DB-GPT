#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @2023 AI, ZHIHU Inc. (zhihu.com)
#
# @author: ouzebin <ouzebin@zhihu.com>
# @date: 2023/08/07
import argparse
import os


def build_index(path):
    data_path = os.path.join(path, "data.jsonl")
    assert os.path.exists(data_path), f"Jsonline dataset '{data_path}' not found."

    offset = 0
    starts = [offset]
    with open(data_path, "rb") as fin:
        for line in fin:
            offset += len(line)
            starts.append(offset)
    with open(os.path.join(path, "index"), "w") as fout:
        for s in starts:
            fout.write(f"{s}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", required=True, help="Data path.")
    args = parser.parse_args()
    build_index(args.path)
