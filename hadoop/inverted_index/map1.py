#!/usr/bin/env python3
"""Map 1: Parse words into docid word \t 1 for each document."""

import sys
import re
import csv
import json


csv.field_size_limit(sys.maxsize)
# 1. Combine both document title and document body by concatenating them, separated by a space.

# 2. Remove non-alphanumeric characters (that also aren’t spaces) like this:
# import re
# text = re.sub(r"[^a-zA-Z0-9 ]+", "", text)

# 3. The inverted index should be case insensitive. Convert upper case characters to lower case using casefold().

# 4. Split the text into whitespace-delimited terms.

# 5. Remove stop words. We have provided a list of stop words in hadoop/inverted_index/stopwords.txt.

STOP_WORDS = []
stop_words_path = './stopwords.txt'
with open(stop_words_path, encoding='utf-8') as stop_words_file:
    for line in stop_words_file:
        STOP_WORDS.append(line.strip().casefold())

for doc in csv.reader(sys.stdin):
    if not doc:
        continue
    # print(f"{doc}")
    # doc_info = list(csv.reader([doc]))[0]
    doc_id = doc[0]
    doc_title = doc[1]
    doc_body = doc[2]

    # tmp = 0
    # doc_id = doc_info[0][0]
    # if doc_info[2 + tmp][0] == '':
    #     tmp += 1
    # doc_title = doc_info[2 + tmp][0]
    # if doc_info[4 + tmp][0] == '':
    #     tmp += 1
    # doc_body = doc_info[4 + tmp][0]

    # Concatenat document title and document body
    doc_title_body = doc_title + " " + doc_body

    # Remove non-alphanumeric characters
    WORD_RE = r"[^a-zA-Z0-9 ]+"
    doc_id = re.sub(WORD_RE, "", doc_id)
    doc_title_body = re.sub(WORD_RE, "", doc_title_body)
    doc_title_body = re.sub(r"[ ]+", " ", doc_title_body)

    # Convert upper case characters to lower case
    doc_id = doc_id.casefold()
    doc_title_body = doc_title_body.casefold()

    # Split the text into whitespace-delimited terms
    doc_words = doc_title_body.split()

    # Remove stop words
    word_list = []
    for word in doc_words:
        if word not in STOP_WORDS:
            word_list.append(word)

    # map1: docid \t {word, frequency}
    for word in word_list:
        value = json.dumps({
            "doc_id": doc_id,
            "tf": 1
            })
        print(f"{word}\t{value}")
        # print(f"{word}\t{doc_id}\t1")

    # # print(doc_id)
    # # print(doc_words)
