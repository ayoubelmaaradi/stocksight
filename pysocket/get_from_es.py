try:
    from elasticsearch5 import Elasticsearch
except ImportError:
    from elasticsearch import Elasticsearch


es = Elasticsearch(['http://127.0.0.1:9200/'])
doc = {
    'size' : 10000,
    'query': {
        'match_all' : {}
    }
}

res = es.search(index="stocksight", doc_type='stock', body=doc,scroll='1m')
scroll = res['_scroll_id']
res2 = es.scroll(scroll_id = scroll, scroll = '1m')










