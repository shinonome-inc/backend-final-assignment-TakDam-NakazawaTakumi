import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Tweet(models.Model):
    id = models.UUIDField(primary_key=True, blank=True, null=False, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="author", on_delete=models.CASCADE, default="")
    title = models.CharField(max_length=50)

    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
