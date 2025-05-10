"""In order to use different settings for django in development and production builds we use this file to switch between two different configurations."""

import os

env = os.environ.get("DJANGO_PIPELINE", default="development")

if env == "production":
    from .settings_production import *
else:
    from .settings_development import *
