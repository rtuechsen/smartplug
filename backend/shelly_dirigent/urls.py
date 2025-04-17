from django.urls import path, include
from . import views
from django.contrib import admin
import django_eventstream

urlpatterns = [
    path("admin/", admin.site.urls),  # TODO: remove ???
    path("api/csrf/", views.csrf),
    path("api/ping/", views.ping),
	path("api/events/", include(django_eventstream.urls), {"channels": ["test"]}),
]
