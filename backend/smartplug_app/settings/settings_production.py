"""Settings for production builds."""

import os
from .settings_base import *

# don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# keep the secret key used in production secret!
# TODO: change secret key
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "your-production-secret-key")

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
