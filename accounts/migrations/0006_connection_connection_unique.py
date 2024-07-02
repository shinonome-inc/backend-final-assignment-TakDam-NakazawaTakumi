# Generated by Django 4.2.11 on 2024-07-02 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_remove_connection_user_connection_following_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="connection",
            constraint=models.UniqueConstraint(fields=("follower", "following"), name="connection_unique"),
        ),
    ]
