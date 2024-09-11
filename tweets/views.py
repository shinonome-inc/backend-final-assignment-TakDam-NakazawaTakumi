from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from accounts.models import User

from .forms import TweetCreationForm
from .models import Favorite, Tweet


@login_required
def home_view(request):
    tweets = Tweet.objects.select_related("user")
    favorites = Favorite.objects.all().select_related("tweet").select_related("user")
    tweets_list = tweets.all()
    tweets_count = tweets_list.count()
    i = 0
    for tweet in tweets_list:
        tweet.n_liked = favorites.filter(tweet=tweet).prefetch_related("tweet").count()
        tweet.index = i + 1
        i += 1
        for favorite in favorites:
            if favorite.user == request.user and favorite.tweet == tweet:
                tweet.liked = True
                break
            else:
                tweet.liked = False
    context = {"tweets_list": tweets_list, "tweets_count": tweets_count}
    return render(request, "tweets/home.html", context)


@login_required
def tweetdetail_view(request, pk):
    tweets = Tweet.objects.select_related("user").filter(id=pk)
    if Favorite.objects.filter(user=request.user, tweet=tweets[0]).exists():
        liked = True
    else:
        liked = False
    n_liked = Favorite.objects.filter(tweet=tweets[0]).all().count()
    return render(request, "tweets/detail.html", {"tweets": tweets, "liked": liked, "n_liked": n_liked})


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
        Favorite.objects.get_or_create(user=user, tweet=tweet)
        context = {
            "id": pk,
            "liked": True,
            "n_liked": Favorite.objects.filter(tweet=tweet).all().count(),
        }
        return JsonResponse(context)


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
        context = {
            "id": pk,
            "liked": False,
            "n_liked": Favorite.objects.filter(tweet=tweet).all().count(),
        }
        return JsonResponse(context)
