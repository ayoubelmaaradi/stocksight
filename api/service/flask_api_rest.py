from threading import Thread
from flask import Flask
from flask_cors import CORS
from flask_jsonpify import jsonify
from flask_restful import Resource, Api

from rest.service.es_dao import get_top_tweets, get_tweets_of_search_query, get_news_headlines
from rest.service.news_headlines import main_news_headlines
from rest.service.twitter_search_query import query_through_search

app = Flask(__name__)
api = Api(app)

CORS(app)
def news_daemon():
    news_headlines_thread = Thread(target=main_news_headlines)
    news_headlines_thread.setDaemon(True)
    news_headlines_thread.start()

@app.route("/")
def hello():
    return jsonify({'text': 'Hello World!', 'Message': 'Tweets by API'})


class TopTweets(Resource):
    def get(self):
        return jsonify(get_top_tweets())


class TwitterSearchQuery(Resource):
    def get(self, keyword):
        print('key-word id:' + keyword)
        query_through_search(str(keyword).encode('utf-8').strip())
        return jsonify(get_tweets_of_search_query())

class NewsHeadLines(Resource):
    def get(self):
        return jsonify(get_news_headlines())

api.add_resource(TopTweets, '/api/top_tweets')  # Route_1
api.add_resource(NewsHeadLines, '/api/newsheadlines')  # Route_2
api.add_resource(TwitterSearchQuery, '/api/twittersearchquery/<keyword>')  # Route_3

if __name__ == '__main__':
    news_daemon()
    app.run(port=9090)
