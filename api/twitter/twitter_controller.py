import ast
import datetime
import json
import os

from flask import Blueprint, request
import redis
from flask_jsonpify import jsonpify
from redis import Redis

from api.service.twitter_search_query import query_through_search
from api.twitter.twitter_service import get_list_news_headlines, news_daemon

bp = Blueprint('twitter', __name__, url_prefix='/twitter')
redis_conn = redis.Redis(host='localhost', port=6379, db=0)


@bp.route('/latest_news')
def get_last_news():
    list_of_to_tweets = []
    for i in range(0, redis_conn.llen('news_headlines')):
        tweet = redis_conn.lindex('news_headlines', i)
        res = ast.literal_eval(tweet.decode('utf-8'))
        list_of_to_tweets.append(res)
        print('------------', tweet.decode('utf-8'))
    return jsonpify(list_of_to_tweets)


# require news_headlines.py runned
@bp.route('/search', methods=['GET'])
def search_tweets_query():
    keyword = request.args.get('keyword')
    res = query_through_search(str(keyword).encode('utf-8').strip())
    list_of_to_tweets = []
    # for i in range(0, redis_conn.llen('search_tweets')):
    #     tweet = redis_conn.lindex('search_tweets', i)
    #     #res = ast.literal_eval(tweet)
    #     list_of_to_tweets.append(tweet.decode('utf-8'))
    #     print('------------', tweet.decode('utf-8'))
    return jsonpify(res)


@bp.route('/top_tweets', methods=['GET'])
def top_tweets():
    keyword = request.args.get('keyword')
    keywords = str(keyword).split(',')
    res = query_through_search(str(keywords).encode('utf-8').strip())
    return jsonpify(res)
