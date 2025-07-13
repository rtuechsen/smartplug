"""Contains variables that control the behavior of the backend and provide an
easy way for the systems admin to change key aspects of the backend."""

## Variable used for Development: allows to disable the switching delays.
USE_SWITCHING_DELAYS: bool = True

## A float value in seconds that determines how long to wait before switching a
## recently switched device again.
SWITCHING_TOGGLE_DELAY_SECONDS: float = 1.0

## A float value in seconds that determines how long to wait between switching
## on devices when switching on multiple devices.
INRUSH_CURRENT_DELAY_SECONDS: float = 0.5

## Variable used for Development: allows to disable using the Active Directory
## / LDAP to verify a users identity.\ If disabled any pair of username and
## password matching the pattern configured in openapi.\yaml is accepted, the
## display name of the user in this case is always 'Max Mustermann'.
USE_LDAP: bool = False

## The address of the server running active directory.\ It should start with
## 'ldap://' and end with ':389' (the port for LDAP).
LDAP_SERVER_ADDRESS_AND_PORT: str = "ldap://192.168.58.42:389"

## The time in seconds after which a request to the Active Directory server is
## considered a timeout.
LDAP_TIMEOUT_SECONDS: int = 5

## Variable used for Development: allows to disable sending MQTT messages.\
## When making switch requests these will be treated as successful and return a
## matching response from the MQTTClient.
USE_MQTT: bool = True

## The time in seconds after which a user is signed out if no activity was
## registered.
SESSION_TIMEOUT_SECONDS: int = 120

## The list of addresses (including protocoll and port) the frontend can have.\
## Using http here is okay, since http requests will be forwarded to https by
## nginx.
FRONTEND_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "https://localhost:443",
    "https://127.0.0.1:443",
]

## A list of strings representing the host/domain names that this Django site
## can serve.\ This is a security measure to prevent HTTP Host header attacks.
ALLOWED_HOSTS_LIST: list[str] = ["localhost", "127.0.0.1", "192.168.179.13"]
