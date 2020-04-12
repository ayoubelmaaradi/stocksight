import asyncio
import random
from time import sleep

from aiohttp import web
from sentiment import data
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
async def my_event(sid, message):
    await sio.emit('my_response', {'data': message['data']}, room=sid)


@sio.event
async def my_broadcast_event(sid, message):
    await sio.emit('my_response', {'data': message['data']})


@sio.event
async def join(sid, message):
    sio.enter_room(sid, message['room'])
    await sio.emit('my_response', {'data': 'Entered room: ' + message['room']},
                   room=sid)


@sio.event
async def leave(sid, message):
    sio.leave_room(sid, message['room'])
    await sio.emit('my_response', {'data': 'Left room: ' + message['room']},
                   room=sid)


@sio.event
async def close_room(sid, message):
    await sio.emit('my_response',
                   {'data': 'Room ' + message['room'] + ' is closing.'},
                   room=message['room'])
    await sio.close_room(message['room'])


@sio.event
async def my_room_event(sid, message):
    await sio.emit('my_response', {'data': message['data']},
                   room=message['room'])


@sio.event
async def disconnect_request(sid):
    await sio.disconnect(sid)


@sio.event
async def connect(sid, environ):
    await sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)


decide = True


def val():
    if decide == True:
        return False


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
    await sio.emit('message', data[-1])


@sio.on('message')
async def print_message(sid, message):
    print("Socket ID: ", sid)
    print(message)
    # await a successful emit of our reversed message
    # back to the client
    i = 0
    while (i < 100):
        i = i + 1
        sleep(1)
        await sio.emit('message', {'text': '"\nThis "' + str(i) + '" the first ping"',
                                   'title': 'My title' + str(i),
                                   'content': 'no content for' + str(i)
                                   })


@sio.on('data2')
async def chart_builder():
    decide = val()
    await sio.send(data=[50, random.randint(52, 700), random.randint(52, 700), random.randint(52, 700), 20, 265,
                         random.randint(52, 700), 400])


@sio.event
def disconnect(sid):
    print('Client disconnected')


app.router.add_static('/static', 'static')
app.router.add_get('/', index)
app.router.add_get('/home', home)

if __name__ == '__main__':
    sio.start_background_task(background_task)
    web.run_app(app,host='0.0.0.0')
