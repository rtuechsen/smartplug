"""TODO: module docstring"""

# TODO: store settings here or in settings_base.py ???

SWITCHING_TOGGLE_DELAY = 5.0
"""A float value in seconds that determines how long to wait before switching a
recently switched device again."""

INRUSH_CURRENT_DELAY = 1.0
"""A float value in seconds that determines how long to wait between switching
on devices when switching on multiple devices."""

# TODO: remove, development variable
USE_LDAP: bool = False

LDAP_SERVER_ADDRESS_AND_PORT: str = "ldap://192.168.178.50:389"
"""The address of the server running active directory. It should start with 
'ldap://' and end with ':389' (the port for LDAP).
"""

LDAP_TIMEOUT_SECONDS: int = 5
"""The time in seconds after which a request to the active directory server is 
considered a timeout.
"""

LDAP_SEARCH_BASE_DN = "dc=mylab,dc=local"
"""The search path when looking up information about the users. If the 
User Principle Name was john.doe@mylab.local the LDAP_SEARCH_BASE_DN would be
'dc=mylab,dc=local'.
"""
