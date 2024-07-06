from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.views.generic import CreateView, ListView

from tweets.models import Tweet

from .forms import LoginForm, SignupForm
from .models import Connection, User


class SignupView(CreateView):

    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):

        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class FollowingListView(ListView):
    model = Connection
    template_name = "accounts/following_list.html"
    context_object_name = "following_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            "following_list": Connection.objects.select_related("following").filter(
                follower=User.objects.prefetch_related("following").get(username=self.kwargs["username"])
            ),
            "username": self.kwargs["username"],
        }
        return context


class FollowerListView(ListView):
    model = Connection
    template_name = "accounts/follower_list.html"
    context_object_name = "follower_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            "follower_list": Connection.objects.select_related("follower").filter(
                following=User.objects.prefetch_related("follower").get(username=self.kwargs["username"])
            ),
            "username": self.kwargs["username"],
        }
        return context


@login_required
def userprofile_view(request, username):
    user = User.objects.get(username=username)
    tweets_list = Tweet.objects.select_related("user").filter(user=user)
    n_follower = Connection.objects.select_related("follower").filter(following=user).all().count()
    n_following = Connection.objects.select_related("following").filter(follower=user).all().count()
    return render(
        request,
        "tweets/profile.html",
        {"username": username, "tweets_list": tweets_list, "n_follower": n_follower, "n_following": n_following},
    )


@login_required
def follow_view(request, username):
    try:
        follower = User.objects.get(username=request.user.username)
        following = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseNotFound("User does not exist")
    if follower == following:
        return HttpResponseBadRequest("You cannot follow yourself")
    else:
        created = Connection.objects.get_or_create(follower=follower, following=following)
        if created:
            return redirect("tweets:home")
        else:
            return HttpResponseBadRequest("You are already following this user")


@login_required
def unfollow_view(request, username):
    try:
        follower = User.objects.get(username=request.user.username)
        following = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseNotFound("User does not exist")
    if follower == following:
        return HttpResponseBadRequest("You cannot unfollow yourself")
    else:
        Connection.objects.filter(follower=follower, following=following).delete()
        return redirect("tweets:home")


class LoginView(BaseLoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"


class LogoutView(BaseLogoutView):
    success_url = settings.LOGOUT_REDIRECT_URL
