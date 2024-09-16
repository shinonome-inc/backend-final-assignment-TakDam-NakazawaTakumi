# Generated by Django 4.2.11 on 2024-09-16 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tweets", "0008_alter_favorite_tweet"),
    ]

    operations = [
        migrations.AlterField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_liked",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
