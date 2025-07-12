"""Contains a utility script to generate a secure token."""

import secrets

with open("/etc/django/secret_key_development", "w", encoding="UTF-8") as f:
    f.write(secrets.token_urlsafe(32))

with open("/etc/django/secret_key_production", "w", encoding="UTF-8") as f:
    f.write(secrets.token_urlsafe(32))
