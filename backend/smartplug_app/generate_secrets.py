"""Contains a utility script to generate a secure token."""

import secrets

with open(
    "/etc/django_secret_key_development.txt", "w", encoding="UTF-8"
) as f:
    f.write(secrets.token_urlsafe(32))
