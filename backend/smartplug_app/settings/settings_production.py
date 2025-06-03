"""Settings specific for production builds, these settings extend those from
settings_base.py.
"""

# From settings_base we import all settings shared between development and
# production builds.
from .settings_base import *
import os

# Don't run with debug turned on in production!
DEBUG = False

## The individual secret key of this project (for production builds).\ This
## value is the used to securing signed data.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "your-production-secret-key")
