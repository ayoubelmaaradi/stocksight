from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify

from api.elastic_queries import get_top_tweets

app = Flask(__name__)
api = Api(app)

CORS(app)


@app.route("/")
def hello():
    return jsonify({'text': 'Hello World!', 'Message': 'Tweets by API'})


class TopTweets(Resource):
    def get(self):
        return jsonify(get_top_tweets())


class TweetsByName(Resource):
    def get(self, tweet_id):
        print('Employee id:' + tweet_id)
        result = {'data': {'id': 1, 'name': 'Balram'}}
        return jsonify(result)


api.add_resource(TopTweets, '/top_tweets')  # Route_1
api.add_resource(TweetsByName, '/tweets/<tweet_id>')  # Route_3

if __name__ == '__main__':
    app.run(port=9090)
