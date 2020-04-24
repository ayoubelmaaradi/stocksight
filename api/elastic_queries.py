from builtins import type

from elasticsearch import Elasticsearch

from api.query_dsl_es import query_most_retweeted
from config import elasticsearch_host, elasticsearch_port, elasticsearch_password, elasticsearch_user, \
    elasticsearch_index

es = Elasticsearch(hosts=[{'host': elasticsearch_host, 'port': elasticsearch_port}],
                       http_auth=(elasticsearch_user, elasticsearch_password))

# res = es.get(index=elasticsearch_index, id=1)
# print(res['_source'])

#es.indices.refresh(index=elasticsearch_index)

res = es.search(index=elasticsearch_index, body=query_most_retweeted)
#print(res['hits']['hits'][0])
def total_hits():
    for hit in res['hits']['hits']:
        print('-------------------------------------------------------------')
        print(hit["_source"]['author'])
        print(hit["_source"]['location'])
        print(hit["_source"]['message'])
        print(hit["_source"]['sentiment'])
        print(hit["_source"]['date'])

#es.indices.delete(index=elasticsearch_index, ignore=[400, 404])
def get_top_tweets():
    for item in res['aggregations']['top_tags']['buckets']:
        print('---------------------------------')
        print('Tweet', item['key'])
        print('Number of retweets', item['doc_count'])
    return res['aggregations']['top_tags']['buckets']

