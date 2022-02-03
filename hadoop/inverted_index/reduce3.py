#!/usr/bin/env python3
"""Reduce 3: ."""


import sys
import json
import itertools


def reduce_one_group(key, group, flag2):
    """Reduce one group."""
    flag = True
    for line in group:
        word_info = line.strip().split('\t')
        json_str = json.loads(word_info[1])
        if flag:
            flag = False
            if flag2:
                print(f"{json_str['word']} {json_str['idf']}", end='')
            else:
                print(f"\n{json_str['word']} {json_str['idf']}", end='')
        print(f" {json_str['doc_id']} {json_str['tf']} {json_str['norm']}", end='')


def keyfunc(line):
    """Return the key from a TAB-delimited key-value pair."""
    word_info = line.strip().split('\t')
    json_str = json.loads(word_info[1])
    return json_str['word']


def main():
    """Divide sorted lines into groups that share a key."""
    flag = True
    for key, group in itertools.groupby(sys.stdin, keyfunc):
        if flag:
            reduce_one_group(key, group, flag)
            flag = False
        else:
            reduce_one_group(key, group, flag)
    print()


if __name__ == "__main__":
    main()
