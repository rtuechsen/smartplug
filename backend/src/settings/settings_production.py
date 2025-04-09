
from .settings_base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
# TODO
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# SECURITY WARNING: keep the secret key used in production secret!
# TODO
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-production-secret-key')

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
