

from django.urls import path, include
import django_eventstream
from . import views

urlpatterns = [
    path("api/ping/", views.ping),
    path("api/csrf/", views.csrf),
    path("api/csrf/", views.login),
    path("api/csrf/", views.logout),
    path("api/csrf/", views.gettree),
    path("api/csrf/", views.switch),
    path("api/events/", include(django_eventstream.urls), {"channels": ["labor_config"]}),
]
