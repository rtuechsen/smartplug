"""TODO."""

# TODO: remove, development variable
USE_SWITCHING_DELAYS: bool = True

# TODO: add unit (seconds) to time variables
SWITCHING_TOGGLE_DELAY: float = 1.0
"""A float value in seconds that determines how long to wait before switching a
recently switched device again."""

INRUSH_CURRENT_DELAY: float = 0.5
"""A float value in seconds that determines how long to wait between switching
on devices when switching on multiple devices."""

# TODO: remove, development variable
USE_LDAP: bool = False

# TODO: use correct host name
LDAP_SERVER_ADDRESS_AND_PORT: str = "ldap://192.168.133.42:389"
"""The address of the server running active directory.

It should start with
'ldap://' and end with ':389' (the port for LDAP).
"""

LDAP_TIMEOUT_SECONDS: int = 5
"""The time in seconds after which a request to the active directory server is
considered a timeout."""

# TODO remove, development variable
USE_MQTT: bool = False

SECRET_KEY_DEVELOPMENT: str = (
    "django-insecure-z5_=&6x00u($dv(x4&vhw46(4#ouj2o1ki(zrby=1+bafzvb$j"
)

SECRET_KEY_PRODUCTION: str = "GyB#yNG@!hAdqV75cX3LdVyJ!ubQF4"

SESSION_TIMEOUT_SECONDS: int = 120

# TODO: add comment: http okay because nginx forwards to https
FRONTEND_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "https://localhost:443",
    "https://127.0.0.1:443",
]

ALLOWED_HOSTS_LIST: list[str] = ["localhost", "127.0.0.1", "192.168.133.195"]
