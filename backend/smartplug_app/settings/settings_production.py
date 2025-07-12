"""Settings specific for production builds, these settings extend those from
settings_base.py.
"""

import os

# From settings_base we import all settings shared between development and
# production builds.
from .settings_base import *
from ..admin_settings import SECRET_KEY_PRODUCTION

# Don't run with debug turned on in production!
DEBUG = False

# keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", SECRET_KEY_PRODUCTION)

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
