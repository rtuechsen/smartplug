from django.urls import path
from . import views

urlpatterns = [
    path('api/csrf/', views.csrf),
    path('api/ping/', views.ping),
]