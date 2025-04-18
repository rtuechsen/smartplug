

from django.urls import path, include
import django_eventstream
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    path("api/ping/", views.ping),
    path("api/csrf/", views.csrf),
    path("api/login/", views.login),
    path("api/logout/", views.logout),
    path("api/gettree/", views.gettree),
    path("api/switch/", views.switch),
    # TODO: do we want those endpoints ???
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("api/events/", include(django_eventstream.urls), {"channels": ["labor_config"]}),
]
