# Import the necessary methods from tweepy library
import sys
from datetime import datetime
from json import JSONDecoder
import re

import jsonpickle as jsonpickle
import redis
from elasticsearch import Elasticsearch
from tweepy import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
from tweepy import TweepError

import warnings

import config
from config import elasticsearch_host, elasticsearch_user, elasticsearch_password, elasticsearch_port

warnings.filterwarnings("ignore")
jsonpickle.set_decoder_options('simplejson', encoding='utf8', cls=JSONDecoder)

# Variables that contains the user credentials to access Twitter API 
# # keys from  "Twitter Tweet Summarization" app
CONSUMER_KEY = 'p9smvhLm9SXh9z2EUNYyakFe7'
CONSUMER_SECRET = 'Fu6f5YWPyEfrUwpGS02Ojm2eMSxanySYzvkhP7ypVLtlCvIvgy'
ACCESS_TOKEN = '809287937351249920-2S2imOpJVEy0oxDlGwVADh3wM2WPVpY'
ACCESS_TOKEN_SECRET = 'EkF2JQx9jcsBOyyMU4UsZYgFqLWJ1UH0W8NCDPL7Axnbs'
redis_conn = redis.Redis(host='localhost', port=6379, db=0)
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
DATA_FOLDER = './'
es = Elasticsearch(hosts=[{'host': elasticsearch_host, 'port': elasticsearch_port}],
                   http_auth=(elasticsearch_user, elasticsearch_password))

lis_research = []


# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status):
        print(status)


def query_through_stream(topic):
    stream = Stream(auth, l)
    stream.filter(track=[topic])


def query_through_search(query):
    TOPIC_DATA_HANDLER = open(str(DATA_FOLDER) + str(query), 'w')
    api = API(auth)

    tweets = dict()
    # # Initialization ##
    max_tweets = 400
    tweet_count = 0
    max_id = -1
    since_id = None
    tweet_per_query = 200

    # print("Downloading tweets for query : "+query)
    while tweet_count < max_tweets:
        try:
            if (max_id <= 0):
                if (not since_id):
                    new_tweets = api.search(q=query, count=tweet_per_query, lang="en", result_type="mixed", locale="en")
                else:
                    new_tweets = api.search(q=query, count=tweet_per_query, since_id=since_id, lang="en",
                                            result_type="mixed", locale="en")
            else:
                if (not since_id):
                    new_tweets = api.search(q=query, count=tweet_per_query, max_id=str(max_id - 1), lang="en",
                                            result_type="mixed", locale="en")
                else:
                    new_tweets = api.search(q=query, count=tweet_per_query, max_id=str(max_id - 1), since_id=since_id,
                                            lang="en", result_type="mixed", locale="en")
            if not new_tweets:
                print("No more tweets found")
                break
            tweet_id_iter = None
            for tweet in new_tweets:
                json_tweet = jsonpickle.encode(tweet._json, unpicklable=False)
                if (tweet.user.followers_count > 1000 and tweet.text not in tweets):
                    #tweet_text = (tweet.text).encode('utf-8').strip()
                    tweet_text = clean_text(str(tweet.text))#.replace('\n', ' ')
                    tweet_text = clean_text_sentiment(str(tweet_text))#.replace('\n', ' ')

                    tweets[tweet.text] = 1  # # for duplicate identification

                    TOPIC_DATA_HANDLER.write(str(tweet_text) + '\n\n')
                    tweet_count += 1
                    if (tweet_id_iter):
                        tweet_id_iter = min(tweet_id_iter, tweet.id)
                    else:
                        tweet_id_iter = tweet.id
                    if (tweet_count == max_tweets):
                        break
                    es.index(index=config.elasticsearch_index, doc_type='tweets', body={
                        'text': tweet_text,
                        'date': datetime.now()
                    })

                    lis_research.append({
                        'text': tweet_text,
                        'date': datetime.now()
                    })
                    # lis_research.append(json_tweet)

            tweet_count += len(new_tweets)
            print("Downloaded {0} tweets".format(tweet_count))
            redis_conn.rpush("search_tweets", lis_research)
            # max_id = new_tweets[-1].id
            max_id = tweet_id_iter
        except TweepError as e:
            print("some error : " + str(e))
            break
    return lis_research
def clean_text_sentiment(text):
    # clean up text for sentiment analysis
    text = re.sub(r"[#|@]\S+", "", text)
    text = text.strip()
    return text

def clean_text(text):
    # clean up text
    text = text.replace("\n", " ")
    text = re.sub(r"https?\S+", "", text)
    text = re.sub(r"&.*?;", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = text.replace("RT", "")
    text = text.replace(u"…", "")
    text = text.strip()
    return text

def isEnglish(s):
    try:
        s.decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


# if __name__ == '__main__':
#     # This handles Twitter authentication and the connection to Twitter Streaming API
#     TOPICS = 'hashtags.txt'
#     l = StdOutListener()
#     for topic in open(TOPICS, 'r'):
#         # if(isEnglish(topic)):
#         query_through_search('oott'.encode('utf-8').strip())
#         # query_through_stream('oott')
