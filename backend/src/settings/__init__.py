
import os

env = os.environ.get('DJANGO_PIPELINE', default='development')

if env == 'production':
    from .settings_production import *
else:
    from .settings_development import *
    
