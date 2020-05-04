from threading import Thread

import redis

import sched, time

from api.service.es_dao import get_news_headlines, get_top_tweets

# s = sched.scheduler(time.time, time.sleep)
#
#
# def do_sched():
#     s.enter(1000, 2, get_news_headlines)
#     s.enter(1000, 1, get_top_tweets)
#     s.run()
#
#
# def news_daemon():
#     news_headlines_thread = Thread(target=do_sched())
#     news_headlines_thread.setDaemon(True)
#     news_headlines_thread.start()
#
#
# news_daemon()
# s = sched.scheduler(time.time, time.sleep)


# def sched_top_tweets_retriever(sc):
#     print("Doing stuff...")
#     # do your stuff
#     s.enter(60, 1, get_top_tweets, (sc,))


# s.enter(60, 1, get_top_tweets, (s,))
# s.run()

redis_conn = redis.Redis(host='localhost', port=6379, db=0)
list_of_to_tweets = []
for i in range(0, redis_conn.llen('news_headlines')):

    tweet = redis_conn.lindex('news_headlines', i)
    list_of_to_tweets.append(tweet.decode('utf-8'))

    print('------------', tweet.decode('utf-8'))
if len(list_of_to_tweets) == 0:
    print('list null')
