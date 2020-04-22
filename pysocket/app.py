import asyncio
import json
import random
from threading import Thread
from time import sleep

from django.contrib.redirects import apps
from flask import render_template, Flask
from flask_socketio import SocketIO

from sentiment import datalist
import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
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
@app.route('/')
def home():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('home.html')

def do_whatever_processing_you_want(text):
    return ('%s' % (text)).encode('utf-8')


class StdOutListener(StreamListener):
    def __init__(self):
        pass

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            text = do_whatever_processing_you_want(tweet['text'])
            socketio.emit('stream_channel',
                          {'data': text, 'time': tweet[u'timestamp_ms']},
                          namespace='/message')
            print(do_whatever_processing_you_want(text))
        except:
            pass

    def on_error(self, status):
        print('//////// Error status code', status)
        exit()


# async def background_task():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         await sio.sleep(10)
#         count += 1
#         await sio.emit('my_response', {'data': 'Server generated event'})


# async def index(request):
#     with open('app.html') as f:
#         return web.Response(text=f.read(), content_type='text/html')


# async def home(request):
#     with open('home.html') as f:
#         return web.Response(text=f.read(), content_type='text/html')
def background_thread():
    """Example of how to send server generated events to clients."""
    stream = Stream(auth, l)
    _keywords = ['cnn', 'cnbc']
    stream.filter(track=_keywords)

async def disconnect_request(sid):
    await socketio.disconnect(sid)


@socketio.on('message')
async def print_message(sid, message):
    # When we receive a new event of type
    # 'message' through a socket.io connection
    # we print the socket ID and the message
    print("Socket ID: ", sid)
    print(message)


@socketio.on('message')
async def print_message(sid, message):
    print("Socket ID: ", sid)
    print(message)
    # await a successful emit of our reversed message
    # back to the client
    # screen_name = str(dict_data.get("user", {}).get("screen_name"))
    # location = str(dict_data.get("user", {}).get("location"))
    # language = str(dict_data.get("user", {}).get("lang"))
    # friends = int(dict_data.get("user", {}).get("friends_count"))
    # followers = int(dict_data.get("user", {}).get("followers_count"))
    # statuses = int(dict_data.get("user", {}).get("statuses_count"))
    # text_filtered = str(textclean)
    # tweetid = int(dict_data.get("id"))
    # text_raw = str(dict_data.get("text"))

    # await sio.emit('message', datalist[-1])


# @sio.on('message')
# async def print_message(sid, message):
#     print("Socket ID: ", sid)
#     print(message)
#     # await a successful emit of our reversed message
#     # back to the client
#     n = len(datalist)
#     while (datalist is not None):
#         sleep(1)
#         await sio.emit('message', {'text': "uuuuuuu"})


def disconnect(sid):
    print('Client disconnected')


# app.router.add_static('/static', 'static')
# app.router.add_get('/', home)
l = StdOutListener()
if __name__ == '__main__':
    socketio.start_background_task(background_thread())
    socketio.run_app(app, host='0.0.0.0', port=8181)
