"""Contains ... TODO.

TODO: more details ???
"""

import ldap
from rest_framework import status
from rest_framework.request import Request
from django.conf import settings
from .error_handler import BackendError
from .admin_settings import (
    USE_LDAP,
    LDAP_SERVER_ADDRESS_AND_PORT,
    LDAP_TIMEOUT_SECONDS,
)


# TODO: better: SessionManager ???
class LoginManager:

    def __init__(self):
        pass

    def login(self, request: Request) -> None:
        username = request.data.get("username")
        password = request.data.get("password")

        first_name, last_name = self._authenticate(
            username=username, password=password
        )

        request.session["USERNAME"] = username
        request.session["FIRSTNAME"] = first_name
        request.session["LASTNAME"] = last_name
        request.session["HTTP_USER_AGENT"] = request.META["HTTP_USER_AGENT"]
        request.session["HTTP_ACCEPT_LANGUAGE"] = request.META[
            "HTTP_ACCEPT_LANGUAGE"
        ]
        request.session["REMOTE_ADDR"] = request.META["REMOTE_ADDR"]

        # TODO: send SSE event: list of active users

    def logout(self, request: Request) -> None:
        # Flushing the session will delete it and protects
        # from session fixation:
        # https://docs.djangoproject.com/en/5.2/topics/http/sessions/
        request.session.flush()

    # TODO: better name ???
    def get_user_permission(self, request: Request) -> None:
        # user will be None unless logged in. Per default we use a
        # database-backed session management. The session data is
        # stored server-side and referenced by the session-id.
        # https://stackoverflow.com/questions/5113421/what-is-the-difference-between-a-cookie-and-a-session-in-django
        # https://docs.djangoproject.com/en/5.2/topics/http/sessions/

        # We validate the origin of the request. _validate_request_origin()
        # will throw an exception if anything is wrong.
        self._validate_request_origin(request)

        try:
            user = request.session.get("USERNAME")
        except KeyError as e:
            raise BackendError(
                message="A request has been made by a user who is not signed in.",
                status_code=status.HTTP_400_BAD_REQUEST,
                user_message="Authentication failed. Are you signed in?",
            ) from e

        if user:
            # If there is a user and the user needs permission, it means an
            # action happened.
            # We therefor reset the expiry using the value in our settings.
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

    def _authenticate(self, username: str, password: str) -> tuple[str, str]:
        """Verifies that the combination of username and passowrd belongs to a
        user in the Active Directory.

        Tries to retrieve the first and last name of the user from the Active
        Directory as well.

        @param username The username to verify.

        @param password The password to verify.

        @return A tuple with (first name, last name) of the user retrieved from
        the Active Directory.
        """
        # TODO: remove, development code
        if not USE_LDAP:
            if (
                username == "max.mustermann@mylab.local"
                or username == "MYLAB\\mmustermann"
            ) and password == "FHKiel123!":
                return ("Max", "Mustermann")
            else:
                raise BackendError(
                    message=f"Credentials mismatch on user: {username}.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    user_message="Either your password or username were incorrect.",
                )

        try:

            conn = ldap.initialize(LDAP_SERVER_ADDRESS_AND_PORT)

            # debug level 255 is the most verbose
            conn.set_option(ldap.OPT_DEBUG_LEVEL, 255)

            # LDAP 3 is necessary for active directory
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)

            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, LDAP_TIMEOUT_SECONDS)

            # Important for AD: disable referrals
            conn.set_option(ldap.OPT_REFERRALS, 0)

            # The bind performs the actual request to verify the credentials
            conn.simple_bind_s(username, password)

            # next get first and last name of the user (if those exist)

            if "@" in username:
                # UPN = User Principle Name
                # When searching the UPN equals the full email address of the
                # user
                search_filter = f"(userPrincipalName={username})"

                domain_name: str = username.split("@")[1]
                base_dn: str = ",".join(
                    [f"dc={dc}" for dc in domain_name.split(".")]
                )

                # sn = surname
                search_attributes: list[str] = ["givenName", "sn"]

                result = conn.search_s(
                    base_dn,
                    ldap.SCOPE_SUBTREE,
                    search_filter,
                    search_attributes,
                )

                _, entry = result[0]

                # Note: Active Directory apparently requires either the first name
                # or the last name when creating a user

                if "givenName" in entry:
                    first_name = entry["givenName"][0].decode("utf-8")
                else:
                    first_name = ""

                if "sn" in entry:
                    last_name = entry["sn"][0].decode("utf-8")
                else:
                    last_name = ""

            else:
                # Note: When using NetBIOS the base dn the credentials belong
                # to cannot be deduced -> simply display the username in the
                # frontend
                first_name = username.split("\\")[1]
                last_name = ""

            # TODO: should we unbind as well if error happens after binding?
            conn.unbind_s()

            return (first_name, last_name)

        except ldap.INVALID_CREDENTIALS as e:
            raise BackendError(
                message=f"Credentials mismatch on user: {username}.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                user_message="Either your password or username were incorrect.",
            ) from e

        except ldap.LDAPError as e:
            raise BackendError(
                message=f"LDAP bind failed: {e}",
                user_message="Verifying credentials using Active Directory "
                "failed. Please contact the admin.",
            ) from e

    def _validate_request_origin(self, request: Request) -> None:
        # Check that the values from the start of the session match
        # with the values of this request.
        try:
            # This data has been set on login and will be checked when verifying
            # the request origin.
            user_agent = request.session["HTTP_USER_AGENT"]
            accept_language = request.session["HTTP_ACCEPT_LANGUAGE"]
            ip_address = request.session["REMOTE_ADDR"]

            # Compare request header to origin of login.
            if all(
                [
                    user_agent == request.META.get("HTTP_USER_AGENT"),
                    accept_language
                    == request.META.get("HTTP_ACCEPT_LANGUAGE"),
                    ip_address == request.META.get("REMOTE_ADDR"),
                ]
            ):
                return

            raise BackendError(
                message=f"Request origin mismatch on user: {request.session['USERNAME']}.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # TODO: the comment does not match the error message ?!
        # KeyError occurs when the request is missing necessary data for
        # verification.
        except KeyError as e:
            raise BackendError(
                message="A request has been made by a user who is not signed in.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                user_message="Authentication failed. Are you signed in?",
            ) from e
