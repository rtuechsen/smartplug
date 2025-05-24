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
    """TODO"""

    def authenticate(
        self, request: Request, username: str = None, password: str = None
    ) -> User:

        first_name, last_name = self._authenticate_ldap(username, password)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(
                username=username, first_name=first_name, last_name=last_name
            )
            user.save()

        # store data about the user in the session
        request.session["USERNAME"] = username
        request.session["FIRSTNAME"] = first_name
        request.session["LASTNAME"] = last_name
        request.session["HTTP_USER_AGENT"] = request.META["HTTP_USER_AGENT"]
        request.session["HTTP_ACCEPT_LANGUAGE"] = request.META[
            "HTTP_ACCEPT_LANGUAGE"
        ]
        request.session["REMOTE_ADDR"] = request.META["REMOTE_ADDR"]

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _authenticate_ldap(
        self, username: str, password: str
    ) -> tuple[str, str]:
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

        # TODO: need to get either logon name or UPN from ldap, use the same
        # kind no matter what kind of login was used to ensure it gets mapped
        # to the same user

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

                # Note: Active Directory apparently requires either the first
                # name or the last name when creating a user

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
