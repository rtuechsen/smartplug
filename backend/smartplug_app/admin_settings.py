"""TODO."""

# TODO: store settings here or in settings_base.py ???

# TODO: remove, development variable
USE_LDAP: bool = True

# TODO: use correct host name
LDAP_SERVER_ADDRESS_AND_PORT: str = "ldap://192.168.178.50:389"
"""The address of the server running active directory.

It should start with
'ldap://' and end with ':389' (the port for LDAP).
"""

LDAP_TIMEOUT_SECONDS: int = 5
"""The time in seconds after which a request to the active directory server is
considered a timeout."""
