"""Settings specific for development builds.\ These settings extend those from
settings_base.py.
"""

# From settings_base we import all settings shared between development and
# production builds.
from .settings_base import *

DEBUG = True

SECRET_KEY = (
    "django-insecure-z5_=&6x00u($dv(x4&vhw46(4#ouj2o1ki(zrby=1+bafzvb$j"
)
