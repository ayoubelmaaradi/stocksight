from time import sleep
import os
from django.http import HttpResponse
import socketio
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

async_mode = None


class HomePageView(TemplateView):
    template_name = 'pages/home.html'


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class IndexPageView(TemplateView):
    template_name = 'pages/index.html'
    from time import sleep
    # sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
    # app = web.Application()
    # sio.attach(app)

    basedir = os.path.dirname(os.path.realpath(__file__))
    sio = socketio.Server(async_mode='eventlet')

    @sio.event
    async def disconnect_request(self, sid):
        await self.sio.disconnect(sid)

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

        # await sio.emit('message', datalist[-1])

    @sio.on('getdata')
    async def print_message(self, sid, message):
        print("Socket ID: ", sid)
        print(message)
        # await a successful emit of our reversed message
        # back to the client
        while (True):
            sleep(1)
            await self.sio.emit('message', {"text": "resrrr"})

    @sio.event
    def disconnect(sid):
        print('Client disconnected')

# class TweetView(CreateView):
#     model = Tweet
#     fields = ['text']
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super(Tweet, self).form_valid(form)
