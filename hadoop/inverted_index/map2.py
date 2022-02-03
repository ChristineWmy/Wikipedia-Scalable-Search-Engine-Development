#!/usr/bin/env python3
"""Map 2: Calculate tf, idf and norm for each term in each doc."""

import sys
import math
import json


# N: number of documents
with open('total_document_count.txt', encoding='utf-8') as total_doc_file:
    for line in total_doc_file:
        N = float(line)
# print(N)

for line in sys.stdin:
    word_info = line.strip().split('\t')
    json_str = json.loads(word_info[1])
    word = word_info[0]
    # nk: Number of documents that contain term tk
    nk = float(len(json_str))
    # Inverse document frequency of term tk
    idf = math.log(N / nk, 10)

    for doc_id, tf in json_str.items():
        # The normalization factor stored in idf omits the square root.
        norm = (float(tf) * idf) ** 2
        info_json = json.dumps({
            "word": word,
            "doc_id": doc_id,
            "tf": tf,
            "idf": idf,
            "norm": norm
            }, separators=(",", ":"))
        print(f"{doc_id}\t{info_json}")
