#!/usr/bin/env python3
"""Map 3: ."""

import sys
import json

# Set doc_id % 3 as the output key
for line in sys.stdin:
    word_info = line.strip().split('\t')
    json_str = json.loads(word_info[1])
    key = int(word_info[0]) % 3
    id_tf_pair_json = json.dumps(json_str, separators=(',', ':'))
    print(f"{key}\t{id_tf_pair_json}")
