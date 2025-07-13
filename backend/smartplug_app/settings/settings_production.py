"""Settings specific for production builds, these settings extend those from
settings_base.py.
"""

import os

# From settings_base we import all settings shared between development and
# production builds.
from .settings_base import *

# Don't run with debug turned on in production!
DEBUG = False

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
