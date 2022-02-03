"""Index search page view."""

import threading
# import concurrent.futures
import heapq
import queue
import requests
import flask
import search


def get_info(search_url, thread_result_queue):
    """Put the results get from api into queue."""
    return thread_result_queue.put(requests.get(search_url))


def keyfunc(hits):
    """Key function for heapq.merge."""
    return hits['score']


def get_doc_info(context, doc_id):
    """Get doc info from database."""
    connection = search.model.get_db()
    cur = connection.execute(
        "SELECT url as doc_url, "
        "title as doc_title, summary as doc_summary "
        "FROM Documents "
        "WHERE docid = ?", (doc_id,))
    context['results'].append(cur.fetchone())
    return context


@search.app.route('/', methods=['GET'])
def show_index():
    """Display / route."""
    queries = flask.request.args.get("q", type=str)
    initial = True
    if queries == '':
        initial = True
    elif not queries:
        initial = False
        queries = ''
    weight = flask.request.args.get("w", default=0.5)
    context = {
        "query": queries,
        "weight": weight,
        "results": [],
        "initial": initial
    }

    if queries:
        # query_list = queries.split()
        # query_join = "+".join(query_list)
        query_join = "+".join(queries.split())
        threads = []
        thread_result_queue = queue.Queue()
        # Create three threads for index servers
        for i in \
                range(len(search.app.config['SEARCH_INDEX_SEGMENT_API_URLS'])):
            search_url = \
                search.app.config['SEARCH_INDEX_SEGMENT_API_URLS'][i] + \
                "?q=" + query_join + "&w=" + str(weight)
            # Save the results get from threads into queue
            thread = threading.Thread(target=get_info,
                                      args=(search_url, thread_result_queue))
            threads.append(thread)
            thread.start()
        # Close threads
        for thread in threads:
            thread.join()
        results_list = []
        while not thread_result_queue.empty():
            hits_info = thread_result_queue.get().json()
            result_list = []
            for hit in hits_info['hits']:
                result_list.append(hit)
            results_list.append(result_list)
        # print(results_list)

        count = 0
        for hit in heapq.merge(*results_list, key=keyfunc, reverse=True):
            count += 1
            context = get_doc_info(context, int(hit['docid']))
            if count == 10:
                break

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     merge_result = heapq.merge()
        #     for i in \
        #           range(len(search.app.config['SEARCH_INDEX_SEGMENT_API_URLS'])):
        #         search_url = \
        #             search.app.config['SEARCH_INDEX_SEGMENT_API_URLS'][i] + \
        #             "?q=" + query_join + "&w=" + weight
        #         future = executor.submit(get_info, search_url)
        #         return_value_json = future.result().json()
        #         print(return_value_json)
        #         merge_result.merge(return_value_json['hits'])
        #         # merge_result = heapq.merge(return_value_json['hits'])
        #         for merge in merge_result:
        #             print(merge)

    return flask.render_template("index.html", **context)
