"""REST API for Index."""

import re
import math
import pathlib
import flask
import index


def read_stopwords(index_dir):
    """Read stopwords."""
    stopwords_path = index_dir/"stopwords.txt"
    with open(stopwords_path, encoding='utf-8') as stopwords:
        data = stopwords.read()
        index.app.config["STOPWORDS"] = data.split()


def read_pagerank(index_dir):
    """Read pagerank."""
    pagerank_path = index_dir/"pagerank.out"
    with open(pagerank_path, encoding='utf-8') as pagerank:
        for line in pagerank:
            line = line.rstrip()
            doc_id, prank = line.split(",")
            index.app.config["PAGERANK"][int(doc_id)] = float(prank)


def read_inverted_index(index_dir):
    """Read inverted_index."""
    inverted_index_path = \
        index_dir/"inverted_index"/index.app.config["INDEX_PATH"]
    with open(inverted_index_path, encoding='utf-8') as inverted_index:
        for line in inverted_index:
            line = line.rstrip()
            line = line.split()
            term = line[0]
            idf = line[1]
            docs = []
            for i in range(2, len(line), 3):
                docs.append({
                    "id": int(line[i]),
                    "tf": int(line[i + 1]),
                    "norm": float(line[i + 2])
                })
            index.app.config["INVERTED_INDEX"][term] = {
                "idf": float(idf),
                "docs": docs
            }


def get_query_vector(query):
    """Get query vectors."""
    query_vector = []
    query_tf = {}
    # calculate the tf
    for query_term in query:
        if query_term not in query_tf:
            query_tf[query_term] = 1
        else:
            query_tf[query_term] += 1
    # calculate tf*idf for each term
    norm_sum = 0
    for query_term in query:
        idf = index.app.config["INVERTED_INDEX"][query_term]["idf"]
        query_vector.append(query_tf[query_term] * idf)
        norm_sum += (query_tf[query_term] * idf)**2
    norm_term = math.sqrt(norm_sum)
    return [entry/norm_term for entry in query_vector]


def get_valid_docs(query):
    """Get a list of docid where doc contain all the query's term."""
    docs_candidate = {}
    # calculate how many time query appear in a given potential docs
    for query_term in query:
        for doc in index.app.config["INVERTED_INDEX"][query_term]["docs"]:
            docid = doc["id"]
            if docid in docs_candidate:
                docs_candidate[docid] += 1
            else:
                docs_candidate[docid] = 1
    # return [docid for docid in docs_candidate
    #         if docs_candidate[docid] == len(query)]
    return [docid for docid, query_all in docs_candidate.items()
            if query_all == len(query)]


def get_docs_vector(query):
    """Calculate document vectors that contain query term."""
    docs_vector = {}
    docs_norm = {}
    # get a list of valid docs
    valid_docs = get_valid_docs(query)
    # indx keep track of which position on the vector we are on
    docs_vector = {docid: [0] * len(query) for docid in valid_docs}
    for indx, query_term in enumerate(query):
        for doc in index.app.config["INVERTED_INDEX"][query_term]["docs"]:
            doc_id = doc["id"]
            if doc_id in valid_docs:
                term_frequency = doc["tf"]
                idf = index.app.config["INVERTED_INDEX"][query_term]["idf"]
                docs_vector[doc_id][indx] = term_frequency * idf
                docs_norm[doc_id] = doc["norm"]
    # Normalize the vector
    for doc_id, vector in docs_vector.items():
        norm_term = math.sqrt(docs_norm[doc_id])
        docs_vector[doc_id] = [entry/norm_term for entry in vector]
    return docs_vector


def cleanse_query(query):
    """Cleanse the query."""
    # Remove non-alphanumeric characters
    word_re = r"[^a-zA-Z0-9 ]+"
    query = re.sub(word_re, "", query)
    # Convert upper case characters to lower case
    query = query.casefold()
    # Split the text into whitespace-delimited terms
    doc_words = query.split()
    # Remove stop words
    word_list = []
    for word in doc_words:
        if word not in index.app.config["STOPWORDS"]:
            word_list.append(word)
    return word_list


def valid_query(query):
    """Make sure all term in query are contained."""
    for query_term in query:
        if query_term not in index.app.config["INVERTED_INDEX"]:
            return False
    return True


def get_tfidf(vector1, vector2):
    """Calcualte tfidf scores."""
    sum_value = 0
    # for i in range(len(vector1)):
    #     sum_value += vector1[i] * vector2[i]
    for i, vector1_value in enumerate(vector1):
        sum_value += vector1_value * vector2[i]
    return sum_value


def get_scores(query_vec, docs_vec, weight):
    """Get scores."""
    result = []
    for doc_id, vector in docs_vec.items():
        page_rank = index.app.config["PAGERANK"][doc_id]
        tfidf = get_tfidf(query_vec, vector)
        score = weight * page_rank + (1 - weight) * tfidf
        result.append({
            "docid": doc_id,
            "score": score
        })
    return result


@index.app.before_first_request
def startup():
    """Load inverted index, pagerank, and stopwords into memory."""
    index_dir = pathlib.Path(__file__).parent.parent
    read_stopwords(index_dir)
    read_pagerank(index_dir)
    read_inverted_index(index_dir)


@index.app.route('/api/v1/', methods=['GET'])
def get_index():
    """Return index."""
    context = {
        "hits": "/api/v1/hits/",
        "url": flask.request.path
    }
    return flask.jsonify(**context)


@index.app.route('/api/v1/hits/', methods=['GET'])
def get_hits():
    """Return hits."""
    # Get weight from query string with default = 0.5
    weight = flask.request.args.get("w")
    if weight is None:
        weight = 0.5
    else:
        weight = float(weight)
    # Get query from query string
    query = flask.request.args.get("q")
    query = cleanse_query(query)
    if not valid_query(query):
        # Invalid query, return empty list
        context = {
            "hits": []
        }
        return flask.jsonify(**context)
    query_vec = get_query_vector(query)
    docs_vec = get_docs_vector(query)
    hits = get_scores(query_vec, docs_vec, weight)
    # sort hits by score then by id
    hits.sort(key=lambda x: (-x["score"], x["docid"]))
    context = {
        "hits": hits
    }
    return flask.jsonify(**context)
