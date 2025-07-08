"""Settings specific for development builds, these settings extend those from
settings_base.py.
"""

# From settings_base we import all settings shared between development and
# production builds.
from .settings_base import *

DEBUG = True

SECRET_KEY = "aadfj<nfefghöafffq"

# with open(
#     "/etc/django_secret_key_development.txt", "r", encoding="UTF-8"
# ) as f:
#     SECRET_KEY = f.read().strip()
