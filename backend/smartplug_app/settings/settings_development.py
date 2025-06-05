"""Settings specific for development builds, these settings extend those from
settings_base.py.
"""

# From settings_base we import all settings shared between development and
# production builds.
from .settings_base import *
from ..admin_settings import SECRET_KEY_DEVELOPMENT

DEBUG = True

SECRET_KEY = SECRET_KEY_DEVELOPMENT
