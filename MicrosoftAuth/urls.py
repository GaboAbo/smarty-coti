from django.urls import path

from .views import (
    microsoft_login,
    microsoft_callback,
    microsoft_logout,
    error,
)

urlpatterns = [
    path("login/", microsoft_login, name="login"),
    path("callback/", microsoft_callback, name="callback"),
    path("logout/", microsoft_logout, name="logout"),
    path("error/", error, name="error"),
]
