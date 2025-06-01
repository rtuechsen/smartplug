"""Contains a backend for authenticating incoming requests."""

import ldap
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.request import Request
from .error_handler import BackendError
from .admin_settings import (
    USE_LDAP,
    LDAP_SERVER_ADDRESS_AND_PORT,
    LDAP_TIMEOUT_SECONDS,
)

# source: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#specifying-authentication-backends


class AuthenticationBackend(BaseBackend):
    """A backend class to integrate custom authentication using LDAP into
    Django.
    """

    def authenticate(
        self, request: Request, username: str = None, password: str = None
    ) -> User:
        """Function to authenticate a given request using username and
        password.

        This function is inherited from BaseBackend and required to be
        implemented.

        @param request The request that requires authentication.

        @param username The username of the user making the request.

        @param password The password of the user making the request.

        @return The user object corresponding to the username and password.
        """

        first_name, last_name = self._authenticate_ldap(username, password)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # If the user does not yet exist in Djangos database a new entry is
            # created.
            user = User(
                username=username, first_name=first_name, last_name=last_name
            )
            user.save()

        request.session["USERNAME"] = username
        request.session["FIRSTNAME"] = first_name
        request.session["LASTNAME"] = last_name

        # We store some data about the user in the session. This is later used
        # to detect cookie theft.
        request.session["HTTP_USER_AGENT"] = request.META["HTTP_USER_AGENT"]
        request.session["HTTP_ACCEPT_LANGUAGE"] = request.META[
            "HTTP_ACCEPT_LANGUAGE"
        ]
        request.session["REMOTE_ADDR"] = request.META["REMOTE_ADDR"]

        return user

    def get_user(self, user_id: int) -> User | None:
        """Function to get the corresponding user object given a user id.

        This function is inherited from BaseBackend and required to be
        implemented.

        @param The id of the user.

        @return The user object corresponding to the given id or None.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _authenticate_ldap(
        self, username: str, password: str
    ) -> tuple[str, str]:
        """Function to verify that the combination of username and password
        belongs to a user in the configured Active Directory.

        It tries to retrieve the first and last name of the user from the
        configured Active Directory as well.

        @param username The username to verify.

        @param password The password to verify.

        @return A tuple with (first name, last name) of the user retrieved from
        the configured Active Directory.
        """
        # TODO: remove, development code
        if not USE_LDAP:
            if (
                username == "max.mustermann@mylab.local"
                or username == "MYLAB\\mmustermann"
            ) and password == "FHKiel123!":
                return ("Max", "Mustermann")
            elif (
                username == "john.doe@mylab.local" and password == "FHKiel123!"
            ):
                return ("John", "")
            else:
                raise BackendError(
                    message=f"Credentials mismatch on user: {username}.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    user_message="Either your password or username were"
                    "incorrect.",
                )

        # TODO: need to get either logon name or UPN from ldap, use the same
        # kind no matter what kind of login was used to ensure it gets mapped
        # to the same user

        try:
            conn = ldap.initialize(LDAP_SERVER_ADDRESS_AND_PORT)

            # TODO: set debugging to 0 in production as it might log user
            # passwords
            conn.set_option(ldap.OPT_DEBUG_LEVEL, 255)

            # LDAP 3 is necessary for active directory.
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)

            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, LDAP_TIMEOUT_SECONDS)

            # Important for AD: disable referrals.
            conn.set_option(ldap.OPT_REFERRALS, 0)

            # Commands required to enable TLS.
            # https://www.python-ldap.org/en/python-ldap-3.4.3/reference/ldap.html?highlight=tls#tls-options
            # conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
            # conn.set_option(ldap.OPT_X_TLS_CACERTFILE, "./cacert.pem")
            # conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
            # conn.start_tls_s()

            # The bind performs the actual request to verify the credentials.
            conn.simple_bind_s(username, password)

            # next get first and last name of the user (if those exist)

            if "@" in username:
                # UPN = User Principle Name
                # For searching, the UPN equals the full email address of the
                # user.
                search_filter: str = f"(userPrincipalName={username})"

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

                # Note: Active Directory apparently requires either the first
                # name or the last name when creating a user. So either of them
                # will be set.

                if "givenName" in entry:
                    first_name = entry["givenName"][0].decode("UTF-8")
                else:
                    first_name = ""

                if "sn" in entry:
                    last_name = entry["sn"][0].decode("UTF-8")
                else:
                    last_name = ""

            else:
                # Note: When using NetBIOS, the base dn that the credentials
                # belong to cannot be deduced -> simply display the username in
                # the frontend.
                first_name = username.split("\\")[1]
                last_name = ""

            conn.unbind_s()

            return (first_name, last_name)

        except ldap.INVALID_CREDENTIALS as e:

            # TODO: should we unbind as well if error happens after binding?
            # conn.unbind_s()

            raise BackendError(
                message=f"Credentials mismatch on user: {username}.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                user_message="Either your password or username were incorrect.",
            ) from e

        except ldap.LDAPError as e:

            # TODO: should we unbind as well if error happens after binding?
            # conn.unbind_s()

            raise BackendError(
                message=f"LDAP bind failed: {e}",
                user_message="Verifying credentials using Active Directory "
                "failed. Please contact the admin.",
            ) from e
