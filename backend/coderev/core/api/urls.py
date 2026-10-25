from django.urls import path

from .csrf import csrf_token


app_name = "core-api"


urlpatterns = [
    path(
        "csrf/",
        csrf_token,
        name="csrf-token",
    ),
]
