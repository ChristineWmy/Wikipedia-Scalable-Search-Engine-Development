#!/usr/bin/env python3
"""
    Reduce 1: Count word frequency and parse words into
    word \t {docid1: frequency1, docid2: frequency2}.
"""

import sys
import json
import itertools


def reduce_one_group(key, group):
    """Reduce one group."""
    TERM_DICT = {}
    for line in group:
        word = line.split('\t')[0]
        value_json = json.loads(line.split('\t')[1])
        doc_id = value_json["doc_id"]
        tf = int(value_json["tf"])
        if word not in TERM_DICT:
            TERM_DICT[word] = {doc_id: tf}
        else:
            if doc_id in TERM_DICT[word]:
                TERM_DICT[word][doc_id] += tf
            else:
                TERM_DICT[word][doc_id] = tf
    for word, id_tf_pair in TERM_DICT.items():
        id_tf_pair_json = json.dumps(id_tf_pair, separators=(',', ':'))
        print(f"{key}\t{id_tf_pair_json}")


def keyfunc(line):
    """Return the key from a TAB-delimited key-value pair."""
    return line.split("\t")[0]


def main():
    """Divide sorted lines into groups that share a key."""
    for key, group in itertools.groupby(sys.stdin, keyfunc):
        reduce_one_group(key, group)


if __name__ == "__main__":
    main()


# with open('./input/test_output1', 'w') as file_write:
#     for word, id_tf_pair in TERM_DICT.items():
#         id_tf_pair_json = json.dumps(id_tf_pair, separators=(',', ':'))
#         file_write.write(f"{word}\t{id_tf_pair_json}\n")
#         print(f"{word}\t{id_tf_pair_json}")
