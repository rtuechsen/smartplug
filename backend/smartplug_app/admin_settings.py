"""TODO: module docstring"""

# TODO: store settings here or in settings_base.py ???

SWITCHING_TOGGLE_DELAY = 5.0
"""A float value in seconds that determines how long to wait before switching a
recently switched device again."""

INRUSH_CURRENT_DELAY = 1.0
"""A float value in seconds that determines how long to wait between switching
on devices when switching on multiple devices."""

# TODO: remove, development variable
USE_LDAP: bool = True

LDAP_SERVER_ADDRESS_AND_PORT: str = "ldap://192.168.178.50:389"
LDAP_TIMEOUT_SECONDS: int = 5
LDAP_SEARCH_BASE_DN = "dc=mylab,dc=local"
