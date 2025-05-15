import ldap
from rest_framework import status
from rest_framework.request import Request
from django.conf import settings
from .error_handler import BackendError
from .admin_settings import USE_LDAP, LDAP_SERVER_ADDRESS_AND_PORT, LDAP_TIMEOUT_SECONDS


# simulates LDAP-Process
# TODO: Implement LDAP


def authenticate(username: str, password: str) -> None:
    
    # TODO: remove, development code
    if not USE_LDAP:
        if username == "user" and password == "pass":
            return

    try:
        conn = ldap.initialize(LDAP_SERVER_ADDRESS_AND_PORT)
        conn.set_option(ldap.OPT_DEBUG_LEVEL, 255)

        # LDAP 3 is necessary for active directory
        conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)

        conn.set_option(ldap.OPT_NETWORK_TIMEOUT, LDAP_TIMEOUT_SECONDS)

        # Important for AD: disable referrals
        conn.set_option(ldap.OPT_REFERRALS, 0)

        conn.simple_bind_s(username, password)

        # get proper name of the user
        # TODO: only works form email, make this work with 'DOMAIN_NAME\user'
        sAMAccountName: str = username.split("@")[0]
        search_attributes: list[str] = ["givenName", "sn"]
        result = conn.search_s(username, ldap.SCOPE_SUBTREE, f"(sAMAccountName={sAMAccountName})", search_attributes)
        
        for dn, entry in result:
            if dn is None:
                continue  # skips LDAP references
            print(f"DN: {dn}")
            for attr, values in entry.items():
                for value in values:
                    print(f"  {attr}: {value.decode('utf-8')}")

        conn.unbind_s()


    except ldap.INVALID_CREDENTIALS as e:
        raise BackendError(
            message=f"Credentials mismatch on user: {username}.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            user_message="Either your password or username were incorrect.",
        ) from e

    # TODO: add more granular exceptions what exactly failed
    except ldap.LDAPError as e:
        raise BackendError(
            message=f"LDAP bind failed: {e}",
            user_message="Verifying credentials using Active Directory failed. "
            "Please contact the admin.",
        ) from e
    


class LoginManager:
    def __init__(self):
        pass

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
                    accept_language == request.META.get("HTTP_ACCEPT_LANGUAGE"),
                    ip_address == request.META.get("REMOTE_ADDR"),
                ]
            ):
                return

            raise BackendError(
                message=f"Request origin mismatch on user: {request.session['USERNAME']}.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # KeyError occurs when the request is missing necessary data for
        # verification.
        except KeyError as e:
            raise BackendError(
                message="A request has been made by a user who is not signed in.",
                status_code=status.HTTP_400_BAD_REQUEST,
                user_message="Authentication failed. Are you signed in?",
            ) from e

        # TODO: Integrate LDAP into login logic

    def login(self, request: Request) -> None:
        username = request.data.get("username")
        password = request.data.get("password")

        authenticate(username=username, password=password)

        request.session["USERNAME"] = username
        request.session["HTTP_USER_AGENT"] = request.META["HTTP_USER_AGENT"]
        request.session["HTTP_ACCEPT_LANGUAGE"] = request.META["HTTP_ACCEPT_LANGUAGE"]
        request.session["REMOTE_ADDR"] = request.META["REMOTE_ADDR"]

    def logout(self, request: Request) -> None:
        # Flushing the session will delete it and protects
        # from session fixation:
        # https://docs.djangoproject.com/en/5.2/topics/http/sessions/
        request.session.flush()

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
            # If there is a user and the user needs permission, it means an action happened.
            # We therefor reset the expiry using the value in our settings.
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
