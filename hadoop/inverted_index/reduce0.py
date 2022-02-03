#!/usr/bin/env python3
"""Reduce 0: sum up all docs."""

import sys


doc_count = 0
for line in sys.stdin:
    doc_count += int(line.partition('\t')[2])
print(doc_count)
