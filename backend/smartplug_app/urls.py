"""Contains the URL patterns the backend implements."""

from django.urls import path, include
import django_eventstream
from . import views

# TODO: use snake_case for functions in views.py (if Django allows that)
# TODO: use snake_case for REST API endpoints as well (if allowed)

## The url patterns for the api (location and name of this variable is mandated
## by Django).
urlpatterns = [
    path("api/csrf/", views.csrf),
    path("api/login/", views.login),
    path("api/logout/", views.logout),
    path("api/gettree/", views.gettree),
    path("api/switch/", views.switch),
    path("api/getusers/", views.getactiveusers),
    path("api/getremainingsessiontime/", views.getremainingsessiontime),
    path(
        "api/events/",
        include(django_eventstream.urls),
        {"channels": ["default"]},
    ),
]
