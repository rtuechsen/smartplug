"""Contains a utility script to generate a secure token."""

from django.core.management.utils import get_random_secret_key

with open("/etc/django/secret_key_development", "w", encoding="UTF-8") as f:
    f.write(get_random_secret_key())

with open("/etc/django/secret_key_production", "w", encoding="UTF-8") as f:
    f.write(get_random_secret_key())
