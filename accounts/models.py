from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField()


class Connection(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        default=None,
    )
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followee", default=None)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="connection_unique"),
        ]

    def __str__(self):
        return f"{self.follower} follows {self.following}"
