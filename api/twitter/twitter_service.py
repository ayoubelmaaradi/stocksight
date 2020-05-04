from threading import Thread

import redis

from api.service.es_dao import get_news_headlines

redis_conn = redis.Redis(host='localhost', port=6379, db=0)


def news_daemon():
    news_headlines_thread = Thread(target=get_news_headlines())
    news_headlines_thread.setDaemon(True)
    news_headlines_thread.start()


def get_list_news_headlines():
    list_of_to_tweets = []
    for i in range(0, redis_conn.llen('news_headlines')):
        tweet = redis_conn.lindex('news_headlines', i)
        list_of_to_tweets.append(tweet)
        print('------------', tweet)
    return list_of_to_tweets



