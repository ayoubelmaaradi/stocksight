import asyncio
import random
from time import sleep

from aiohttp import web
from sentiment import datalist
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit('my_response', {'data': 'Server generated event'})


async def index(request):
    with open('app.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


async def home(request):
    with open('home.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.event
async def disconnect_request(sid):
    await sio.disconnect(sid)

@sio.on('message')
async def print_message(sid, message):
    # When we receive a new event of type
    # 'message' through a socket.io connection
    # we print the socket ID and the message
    print("Socket ID: ", sid)
    print(message)

@sio.on('message')
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

    #await sio.emit('message', datalist[-1])


@sio.on('message')
async def print_message(sid, message):
    print("Socket ID: ", sid)
    print(message)
    # await a successful emit of our reversed message
    # back to the client
    n = len(datalist)
    while (datalist is not None):
        sleep(1)
        await sio.emit('message', datalist[n-1])


@sio.event
def disconnect(sid):
    print('Client disconnected')


app.router.add_static('/static', 'static')
app.router.add_get('/', index)
app.router.add_get('/home', home)

if __name__ == '__main__':
    sio.start_background_task(background_task)
    web.run_app(app,host='0.0.0.0')
