from django.urls import path

from . import views

app_name = "tweets"

urlpatterns = [
    path("home/", views.home_view, name="home"),
    path("create/", views.TweetCreateView.as_view(), name="create"),
    path("<str:pk>/", views.tweetdetail_view, name="detail"),
    path("<str:pk>/delete/", views.tweetdelete_view, name="delete"),
    path("<str:pk>/like/", views.like_view, name="like"),
    path("<str:pk>/unlike/", views.unlike_view, name="unlike"),
]
