from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

class HomePageView(TemplateView):
    template_name = 'pages/home.html'


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'

class IndexPageView(TemplateView):
    template_name = 'pages/index.html'



# class TweetView(CreateView):
#     model = Tweet
#     fields = ['text']
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super(Tweet, self).form_valid(form)
