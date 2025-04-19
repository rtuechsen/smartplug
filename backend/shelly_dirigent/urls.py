

from django.urls import path, include
import django_eventstream
from . import views

urlpatterns = [
    path("api/ping/", views.ping),
    path("api/csrf/", views.csrf),
    path("api/login/", views.login),
    path("api/logout/", views.logout),
    path("api/gettree/", views.gettree),
    path("api/switch/", views.switch),
    path("api/events/", include(django_eventstream.urls), {"channels": ["labor_config"]}),
]
