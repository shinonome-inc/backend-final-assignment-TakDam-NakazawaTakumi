from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from .forms import TweetCreationForm
from .models import Tweet


@login_required
def home_view(request):
    tweets_list = Tweet.objects.select_related("user").all()
    context = {"tweets_list": tweets_list}
    return render(request, "tweets/home.html", context)


@login_required
def tweetdetail_view(request, pk):
    tweets = Tweet.objects.select_related("user").filter(id=pk)
    return render(request, "tweets/detail.html", {"tweets": tweets})


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
