#!/usr/bin/env python3
"""Map 0: Count the total number of documents in the collection."""

import sys

doc_count = 0
for doc in sys.stdin:
    doc_count += 1
print(f"docs\t{doc_count}")
