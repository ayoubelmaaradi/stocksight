import sched
from builtins import type
from datetime import time

import redis
from elasticsearch import Elasticsearch
from threading import Thread

from api.service.es_string_query import query_most_retweeted
from api.service.news_headlines import main_news_headlines
from config import elasticsearch_host, elasticsearch_port, elasticsearch_password, elasticsearch_user, \
    elasticsearch_index

es = Elasticsearch(hosts=[{'host': elasticsearch_host, 'port': elasticsearch_port}],
                   http_auth=(elasticsearch_user, elasticsearch_password))
redis_conn = redis.Redis(host='localhost', port=6379, db=0)
list_top_tweets = []
list_news_headlines = []
# s = sched.scheduler(time.time, time.sleep)
# s.enter(60, 1, get_top_tweets, (s,))
# s.run()

# res = es.get(index=elasticsearch_index, id=1)
# print(res['_source'])

# es.indices.refresh(index=elasticsearch_index)


# print(res['hits']['hits'][0])
def total_hits():
    res = es.search(index=elasticsearch_index, body=query_most_retweeted)
    for hit in res['hits']['hits']:
        print('-------------------------------------------------------------')
        print(hit["_source"]['author'])
        print(hit["_source"]['location'])
        print(hit["_source"]['message'])
        print(hit["_source"]['sentiment'])
        print(hit["_source"]['date'])


# es.indices.delete(index=elasticsearch_index, ignore=[400, 404])
def get_top_tweets():
    res = es.search(index=elasticsearch_index, body=query_most_retweeted)
    i = 0
    for item in res['aggregations']['top_tags']['buckets']:
        # print(item['terms']['hits']['hits'][0]['_source']['date'])
        list_top_tweets.append(item['key'])
    redis_conn.rpush('top_tweets', *list_top_tweets)
    return list


def get_news_headlines():
    list_res = []
    results = es.search(index='stocksight', doc_type='newsheadline', body={
        "query": {
            "match_all": {}
        }
    })
    for hit in results['hits']['hits']:
        print(hit['_source']['message'])
        list_news_headlines.append({'text': hit['_source']['message'], 'date': hit['_source']['date']})
    redis_conn.rpush('news_headlines', *list_news_headlines)
    return list_res


def get_tweets_of_search_query():
    list_res = []
    results = es.search(index='stocksight', doc_type='tweets', body={
        "query": {
            "match_all": {}
        }
    })
    for hit in results['hits']['hits']:
        print(hit['_source']['text'])
        list_res.append({'text': hit['_source']['text'], 'date': hit['_source']['date']})
    return list_res


if __name__ == '__main__':
    # var = get_top_tweets()
    # for elem in var[5:]:
    #     print('------', elem, '-----\n')
    top_tweets_thread = Thread(target=main_news_headlines)
    top_tweets_thread.setDaemon(True)
    top_tweets_thread.start()
