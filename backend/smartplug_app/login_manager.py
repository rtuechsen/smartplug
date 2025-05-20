from rest_framework.request import Request
from django.conf import settings
from .error_handler import BackendError
from rest_framework import status

# simulates LDAP-Process
# TODO: Implement LDAP


def authenticate(username: str, password: str) -> None:
    if username == "user" and password == "pass":
        return

    raise BackendError(
        message=f"Credentials mismatch on user: {username}.",
        status_code=status.HTTP_401_UNAUTHORIZED,
        user_message="Either your password or username were incorrect.",
    )


class LoginManager:
    def __init__(self):
        pass

    def _validate_request_origin(self, request: Request) -> None:
        # Check that the values from the start of the session match
        # with the values of this request.
        try:
            # This data has been set on login and will be checked when
            # verifying the request origin.
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
                message=f"Request origin mismatch on user: "
                f"{request.session['USERNAME']}.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # KeyError occurs when the request is missing necessary data for
        # verification.
        except KeyError as e:
            raise BackendError(
                message="A request has been made by a user who is not signed "
                "in.",
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
        request.session["HTTP_ACCEPT_LANGUAGE"] = request.META[
            "HTTP_ACCEPT_LANGUAGE"
        ]
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
            # If there is a user and the user needs permission, it means an
            # action happened.
            # We therefor reset the expiry using the value in our settings.
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
