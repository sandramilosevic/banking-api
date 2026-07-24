from django.conf import settings
from django.contrib import admin
from django.urls import path
from os import getenv

ADMIN_URL = getenv("ADMIN_URL")

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
]
