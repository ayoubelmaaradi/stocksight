from django.urls import path

from .views import HomePageView, AboutPageView, IndexPageView

urlpatterns = [
    path('home', HomePageView.as_view(), name='home'),
    path('', IndexPageView.as_view(), name='index'),
    path('about/', AboutPageView.as_view(), name='about'),
    # path('timeline/', login_required(views.TimelineView.as_view()), name='timeline'),
    # re_path(r'^user/(?P<username>.+)/', views.UserView.as_view(), name='user_feed')
]
