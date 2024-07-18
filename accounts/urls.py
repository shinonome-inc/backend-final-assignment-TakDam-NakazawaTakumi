from django.urls import path

from . import views
from . import views as auth_views

app_name = "accounts"


urlpatterns = [
    path("signup/", auth_views.SignupView.as_view(), name="signup"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("<str:username>/", views.userprofile_view, name="user_profile"),
    path("<str:username>/follow/", views.follow_view, name="follow"),
    path("<str:username>/unfollow/", views.unfollow_view, name="unfollow"),
    path("<str:username>/following_list/", views.FollowingListView.as_view(), name="following_list"),
    path("<str:username>/follower_list/", views.FollowerListView.as_view(), name="follower_list"),
]
