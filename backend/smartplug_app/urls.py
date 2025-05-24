"""Contains the URL patterns the backend implements."""

from django.urls import path, include
import django_eventstream
from . import views

## The url patterns for the api (location and name of this variable is mandated
## by Django).
urlpatterns = [
    path("api/csrf/", views.csrf),
    path("api/login/", views.login),
    path("api/logout/", views.logout),
    path("api/gettree/", views.gettree),
    path("api/switch/", views.switch),
    path("api/getusers/", views.getusers),
    path(
        "api/events/",
        include(django_eventstream.urls),
        {"channels": ["default"]},
    ),
]
