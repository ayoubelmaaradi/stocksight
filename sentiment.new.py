#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sentiment.py - analyze tweets on Twitter and add
relevant tweets and their sentiment values to
Elasticsearch.
See README.md or https://github.com/shirosaidev/stocksight
for more information.

Copyright (C) Chris Park 2018-2020
stocksight is released under the Apache 2.0 license. See
LICENSE for the full license text.
"""
import tweepy

import config_parser
import sys
import json
import time
import re
from threading import Thread

import requests
import nltk
import argparse
import logging
import string

from flask import Flask, render_template
from flask_socketio import SocketIO

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
from tweepy.streaming import StreamListener
from tweepy import API, Stream, OAuthHandler, TweepError
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup

try:
    from elasticsearch5 import Elasticsearch
except ImportError:
    from elasticsearch import Elasticsearch
from random import randint, randrange
from datetime import datetime
from newspaper import Article, ArticleException

# import elasticsearch host, twitter keys and tokens
from config import *

STOCKSIGHT_VERSION = '0.1-b.10'
__version__ = STOCKSIGHT_VERSION

IS_PY3 = sys.version_info >= (3, 0)

if not IS_PY3:
    print("Sorry, stocksight does not work with Python 2.")
    sys.exit(1)

# sentiment text-processing url
sentimentURL = 'http://text-processing.com/api/sentiment/'
json_tweet = json.dumps({})
# stocksight website url data collector
stocksightURL = 'https://stocksight.diskoverspace.com/data_collector.php'
es = Elasticsearch(hosts=[{'host': elasticsearch_host, 'port': elasticsearch_port}],
                   http_auth=(elasticsearch_user, elasticsearch_password))
# tweet id list
tweet_ids = []

# file to hold twitter user ids
twitter_users_file = './twitteruserids.txt'
cred = {
    # "access_key": "",
    # "access_secret": "",
    # "consumer_key": "",
    # "consumer_secret": ""
    'consumer_key': 'p9smvhLm9SXh9z2EUNYyakFe7',
    'consumer_secret': 'Fu6f5YWPyEfrUwpGS02Ojm2eMSxanySYzvkhP7ypVLtlCvIvgy',
    'access_key': '809287937351249920-2S2imOpJVEy0oxDlGwVADh3wM2WPVpY',
    'access_secret': 'EkF2JQx9jcsBOyyMU4UsZYgFqLWJ1UH0W8NCDPL7Axnbs'
}
auth = tweepy.OAuthHandler(cred['consumer_key'], cred['consumer_secret'])
auth.set_access_token(cred['access_key'], cred['access_secret'])
prev_time = time.time()
sentiment_avg = [0.0, 0.0, 0.0]
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')
datalist = []


def do_whatever_processing_you_want(text):
    return ('%s' % (text)).encode('utf-8')


class TweetStreamListener(StreamListener):
    logger = logging.getLogger('stockinsight')

    def __init__(self):
        self.count = 0
        self.count_filtered = 0
        self.filter_ratio = 0

    # on success
    def on_data(self, data):
        try:
            self.count += 1
            # decode json
            dict_data = json.loads(data)

            print("\n------------------------------> (tweets: %s, filtered: %s, filter-ratio: %s)" \
                  % (self.count, self.count_filtered, str(round(self.count_filtered / self.count * 100, 2)) + "%"))
            self.logger.debug('tweet data: ' + str(dict_data))

            text = dict_data["text"]
            if text is None:
                self.logger.info("Tweet has no relevant text, skipping")
                self.count_filtered += 1
                return True

            # grab html links from tweet
            tweet_urls = []
            if False:  # args.linksentiment:
                tweet_urls = re.findall(r'(https?://[^\s]+)', text)

            # clean up tweet text
            textclean = clean_text(text)

            # check if tweet has no valid text
            if textclean == "":
                self.logger.info("Tweet does not cotain any valid text after cleaning, not adding")
                self.count_filtered += 1
                return True

            # get date when tweet was created
            created_date = time.strftime(
                '%Y-%m-%dT%H:%M:%S', time.strptime(dict_data['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))

            # store dict_data into vars
            screen_name = str(dict_data.get("user", {}).get("screen_name"))
            location = str(dict_data.get("user", {}).get("location"))
            language = str(dict_data.get("user", {}).get("lang"))
            friends = int(dict_data.get("user", {}).get("friends_count"))
            followers = int(dict_data.get("user", {}).get("followers_count"))
            statuses = int(dict_data.get("user", {}).get("statuses_count"))
            text_filtered = str(textclean)
            tweetid = int(dict_data.get("id"))
            text_raw = str(dict_data.get("text"))
            datalist.append(json.dumps(dict_data))
            # output twitter data
            print("\n<------------------------------")
            print("Tweet Date: " + created_date)
            print("Screen Name: " + screen_name)
            print("Location: " + location)
            print("Language: " + language)
            print("Friends: " + str(friends))
            print("Followers: " + str(followers))
            print("Statuses: " + str(statuses))
            print("Tweet ID: " + str(tweetid))
            print("Tweet Raw Text: " + text_raw)
            print("Tweet Filtered Text: " + text_filtered)

            # create tokens of words in text using nltk
            text_for_tokens = re.sub(
                r"[\%|\$|\.|\,|\!|\:|\@]|\(|\)|\#|\+|(``)|('')|\?|\-", "", text_filtered)
            tokens = nltk.word_tokenize(text_for_tokens)
            # convert to lower case
            tokens = [w.lower() for w in tokens]
            # remove punctuation from each word
            table = str.maketrans('', '', string.punctuation)
            stripped = [w.translate(table) for w in tokens]
            # remove remaining tokens that are not alphabetic
            tokens = [w for w in stripped if w.isalpha()]
            # filter out stop words
            stop_words = set(nltk.corpus.stopwords.words('english'))
            tokens = [w for w in tokens if not w in stop_words]
            # remove words less than 3 characters
            tokens = [w for w in tokens if not len(w) < 3]
            print("NLTK Tokens: " + str(tokens))

            # check for min token length
            if len(tokens) < 5:
                self.logger.info("Tweet does not contain min. number of tokens, not adding")
                self.count_filtered += 1
                return True

            # do some checks before adding to elasticsearch and crawling urls in tweet
            if friends == 0 or \
                    followers == 0 or \
                    statuses == 0 or \
                    text == "" or \
                    tweetid in tweet_ids:
                self.logger.info("Tweet doesn't meet min requirements, not adding")
                self.count_filtered += 1
                return True

            # check ignored tokens from config
            for t in nltk_tokens_ignored:
                if t in tokens:
                    self.logger.info("Tweet contains token from ignore list, not adding")
                    self.count_filtered += 1
                    return True
            # check required tokens from config
            tokenspass = False
            tokensfound = 0
            for t in nltk_tokens_required:
                if t in tokens:
                    tokensfound += 1
                    if tokensfound == nltk_min_tokens:
                        tokenspass = True
                        break
            if not tokenspass:
                self.logger.info("Tweet does not contain token from required list or min required, not adding")
                self.count_filtered += 1
                return True

            # clean text for sentiment analysis
            text_clean = clean_text_sentiment(text_filtered)

            # check if tweet has no valid text
            if text_clean == "":
                self.logger.info("Tweet does not cotain any valid text after cleaning, not adding")
                self.count_filtered += 1
                return True

            print("Tweet Clean Text (sentiment): " + text_clean)

            # get sentiment values
            polarity, subjectivity, sentiment = sentiment_analysis(text_clean)

            # add tweet_id to list
            tweet_ids.append(dict_data["id"])

            # get sentiment for tweet
            if len(tweet_urls) > 0:
                tweet_urls_polarity = 0
                tweet_urls_subjectivity = 0
                for url in tweet_urls:
                    res = tweeklink_sentiment_analysis(url)
                    if res is None:
                        continue
                    pol, sub, sen = res
                    tweet_urls_polarity = (tweet_urls_polarity + pol) / 2
                    tweet_urls_subjectivity = (tweet_urls_subjectivity + sub) / 2
                    if sentiment == "positive" or sen == "positive":
                        sentiment = "positive"
                    elif sentiment == "negative" or sen == "negative":
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"

                # calculate average polarity and subjectivity from tweet and tweet links
                if tweet_urls_polarity > 0:
                    polarity = (polarity + tweet_urls_polarity) / 2
                if tweet_urls_subjectivity > 0:
                    subjectivity = (subjectivity + tweet_urls_subjectivity) / 2

            ######## socket
            try:
                tweet = json.loads(data)
                text = do_whatever_processing_you_want(tweet['text'])
                socketio.emit('stream_channel',
                              {'data': text, 'time': tweet[u'timestamp_ms']},
                              namespace='/message')
                print(text)
            except:
                pass
            if not False:  # args.noelasticsearch:
                self.logger.info("Adding tweet to elasticsearch")
                # add twitter data and sentiment info to elasticsearch
                es.index(index='stocksight',  # args.index,
                         doc_type="tweet",
                         body={"author": screen_name,
                               "location": location,
                               "language": language,
                               "friends": friends,
                               "followers": followers,
                               "statuses": statuses,
                               "date": created_date,
                               "message": text_filtered,
                               "tweet_id": tweetid,
                               "polarity": polarity,
                               "subjectivity": subjectivity,
                               "sentiment": sentiment})
                json_tweet = json.dumps({"author": screen_name,
                                         "location": location,
                                         "language": language,
                                         "friends": friends,
                                         "followers": followers,
                                         "statuses": statuses,
                                         "date": created_date,
                                         "message": text_filtered,
                                         "tweet_id": tweetid,
                                         "polarity": polarity,
                                         "subjectivity": subjectivity,
                                         "sentiment": sentiment})

                # randomly sleep to stagger request time
            time.sleep(randrange(2, 5))
            return True

        except Exception as e:
            self.logger.warning("Exception: exception caused by: %s" % e)
            raise

    # on failure
    def on_error(self, status_code):
        self.logger.error("Got an error with status code: %s (will try again later)" % status_code)
        # randomly sleep to stagger request time
        time.sleep(randrange(2, 30))
        return True

    # on timeout
    def on_timeout(self):
        self.logger.warning("Timeout... (will try again later)")
        # randomly sleep to stagger request time
        time.sleep(randrange(2, 30))
        return True


def background_thread():
    l = TweetStreamListener();
    """Example of how to send server generated events to clients."""
    stream = Stream(auth, l)
    _keywords = ['cnn', 'cnbc']
    stream.filter(track=_keywords)

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

def clean_text_sentiment(text):
    # clean up text for sentiment analysis
    text = re.sub(r"[#|@]\S+", "", text)
    text = text.strip()
    return text

def sentiment_analysis(text):
    """Determine if sentiment is positive, negative, or neutral
    algorithm to figure out if sentiment is positive, negative or neutral
    uses sentiment polarity from TextBlob, VADER Sentiment and
    sentiment from text-processing URL
    could be made better :)
    Uploads sentiment to stocksight website.
    """

    # pass text into sentiment url
    # if args.websentiment:
    #     ret = get_sentiment_from_url(text, sentimentURL)
    #     if ret is None:
    #         sentiment_url = None
    #     else:
    #         sentiment_url, neg_url, pos_url, neu_url = ret
    # else:
    sentiment_url = None

    # pass text into TextBlob
    text_tb = TextBlob(text)

    # pass text into VADER Sentiment
    analyzer = SentimentIntensityAnalyzer()
    text_vs = analyzer.polarity_scores(text)

    # determine sentiment from our sources
    if sentiment_url is None:
        if text_tb.sentiment.polarity < 0 and text_vs['compound'] <= -0.05:
            sentiment = "negative"
        elif text_tb.sentiment.polarity > 0 and text_vs['compound'] >= 0.05:
            sentiment = "positive"
        else:
            sentiment = "neutral"
    else:
        if text_tb.sentiment.polarity < 0 and text_vs['compound'] <= -0.05 and sentiment_url == "negative":
            sentiment = "negative"
        elif text_tb.sentiment.polarity > 0 and text_vs['compound'] >= 0.05 and sentiment_url == "positive":
            sentiment = "positive"
        else:
            sentiment = "neutral"

    # calculate average and upload to sentiment website
    # if args.upload:
    #     if sentiment_url:
    #         neg_avg = (text_vs['neg'] + neg_url) / 2
    #         pos_avg = (text_vs['pos'] + pos_url) / 2
    #         neutral_avg = (text_vs['neu'] + neu_url) / 2
    #         upload_sentiment(neg_avg, pos_avg, neutral_avg)
    #     else:
    #         neg_avg = text_vs['neg']
    #         pos_avg = text_vs['pos']
    #         neutral_avg = text_vs['neu']
    #         upload_sentiment(neg_avg, pos_avg, neutral_avg)

    # calculate average polarity from TextBlob and VADER
    polarity = (text_tb.sentiment.polarity + text_vs['compound']) / 2

    # output sentiment polarity
    print("************")
    print("Sentiment Polarity: " + str(round(polarity, 3)))

    # output sentiment subjectivity (TextBlob)
    print("Sentiment Subjectivity: " + str(round(text_tb.sentiment.subjectivity, 3)))

    # output sentiment
    print("Sentiment (url): " + str(sentiment_url))
    print("Sentiment (algorithm): " + str(sentiment))
    print("Overall sentiment (textblob): ", text_tb.sentiment)
    print("Overall sentiment (vader): ", text_vs)
    print("sentence was rated as ", round(text_vs['neg'] * 100, 3), "% Negative")
    print("sentence was rated as ", round(text_vs['neu'] * 100, 3), "% Neutral")
    print("sentence was rated as ", round(text_vs['pos'] * 100, 3), "% Positive")
    print("************")

    return polarity, text_tb.sentiment.subjectivity, sentiment
@app.route('/')
def home():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('flask-socketio-with-twitter/templates/home.html')
if __name__ == '__main__':
    socketio.start_background_task(background_thread())
    socketio.run_app(app, host='0.0.0.0', port=8181)
