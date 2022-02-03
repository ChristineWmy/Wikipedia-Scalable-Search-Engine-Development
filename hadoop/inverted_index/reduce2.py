#!/usr/bin/env python3
"""Reduce 2: Sum up normalization factor for each document."""

import sys
import json
import itertools


def reduce_one_group(key, group):
    """Reduce one group."""
    group = list(group)
    norm_sum = 0
    for line in group:
        word_info = line.strip().split('\t')
        json_str = json.loads(word_info[1])
        norm_sum += float(json_str["norm"])

    for line in group:
        word_info = line.strip().split('\t')
        json_str = json.loads(word_info[1])
        json_str["norm"] = norm_sum
        id_tf_pair_json = json.dumps(json_str, separators=(',', ':'))
        print(f"{key}\t{id_tf_pair_json}")


def keyfunc(line):
    """Return the key from a TAB-delimited key-value pair."""
    return line.strip().split('\t')[0]


def main():
    """Divide sorted lines into groups that share a key."""
    for key, group in itertools.groupby(sys.stdin, keyfunc):
        reduce_one_group(key, group)


if __name__ == "__main__":
    main()
