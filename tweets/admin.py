# from django.contrib import adm        in
from django.contrib import admin

from .models import Favorite, Tweet

admin.site.register(Tweet)
admin.site.register(Favorite)
