"""Settings for development builds."""

from .settings_base import *
from ..admin_settings import SECRET_KEY_DEVELOPMENT

DEBUG = True

SECRET_KEY = SECRET_KEY_DEVELOPMENT
