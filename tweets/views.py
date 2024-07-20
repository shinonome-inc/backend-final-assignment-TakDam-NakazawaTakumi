from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from accounts.models import User

from .forms import TweetCreationForm
from .models import Favorite, Tweet


@login_required
def home_view(request):
    tweets_list = Tweet.objects.select_related("user").all()
    for tweet in tweets_list:
        tweet.n_liked = Favorite.objects.filter(tweet=tweet).all().count()
    context = {"tweets_list": tweets_list}
    return render(request, "tweets/home.html", context)


@login_required
def tweetdetail_view(request, pk):
    tweets = Tweet.objects.select_related("user").filter(id=pk)
    n_liked = Favorite.objects.filter(tweet=tweets[0]).all().count()
    return render(request, "tweets/detail.html", {"tweets": tweets, "n_liked": n_liked})


@login_required
def tweetdelete_view(request, pk):
    tweets = Tweet.objects.filter(id=pk)
    if tweets.count() == 0:
        return HttpResponseNotFound()
    if request.user != tweets[0].user:
        return HttpResponseForbidden()
    tweets.delete()
    return redirect("tweets:home")


class TweetCreateView(LoginRequiredMixin, CreateView):
    template_name = "tweets/post.html"
    form_class = TweetCreationForm
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.created_at = timezone.now()
        return super().form_valid(form)


@login_required
def like_view(request, pk):
    try:
        user = User.objects.get(username=request.user.username)
        tweet = Tweet.objects.get(id=pk)
    except Tweet.DoesNotExist:
        return HttpResponseNotFound("Tweet does not exist")
    else:
        _, created = Favorite.objects.get_or_create(user=user, tweet=tweet)
        return redirect("tweets:home")


@login_required
def unlike_view(request, pk):
    try:
        user = User.objects.get(username=request.user.username)
        tweet = Tweet.objects.get(id=pk)
    except Tweet.DoesNotExist:
        return HttpResponseNotFound("Tweet does not exist")
    except Favorite.DoesNotExist:
        return redirect("tweets:home")
    else:
        Favorite.objects.filter(user=user, tweet=tweet).delete()
        return redirect("tweets:home")
