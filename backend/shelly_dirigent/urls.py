
from .views import RequestManager
from django.contrib import admin
from django.urls import path, include
import django_eventstream

urlpatterns = [
    path("admin/", admin.site.urls),  # TODO: remove ???
    path("api/csrf/", RequestManager.csrf),
    path("api/ping/", RequestManager.ping),
	path("api/events/", include(django_eventstream.urls), {"channels": ["test"]}),
]
