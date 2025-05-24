"""Contains ... TODO.

TODO: more details ???
"""

from rest_framework import status
from rest_framework.request import Request
from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_init
from .error_handler import BackendError
from .sse_tools import send_event


class SessionManager:

    def __init__(self):

        # credit: https://stackoverflow.com/a/4555310

        session_model = apps.get_model("sessions", "Session")
        post_delete.connect(
            self.send_list_of_active_users, sender=session_model
        )
        post_init.connect(self.send_list_of_active_users, sender=session_model)

    def send_list_of_active_users(self, sender, **kwargs):

        session_model = apps.get_model("sessions", "Session")
        user_model = get_user_model()

        active_sessions = session_model.objects.filter(
            expire_date__gt=timezone.now()
        ).iterator()

        active_user_ids = []
        for session in active_sessions:
            session_data = session.get_decoded()
            user_id: str = session_data.get("_auth_user_id")
            if user_id:
                active_user_ids.append(user_id)

        active_users = user_model.objects.filter(id__in=active_user_ids)
        acitve_user_names = [
            f"{user.first_name} {user.last_name}" for user in active_users
        ]
        print(acitve_user_names)

        # send_event(
        #     "default",
        #     "user_list_update",
        #     acitve_user_names,
        # )

    def login(self, request: Request) -> None:

        username = request.data.get("username")
        password = request.data.get("password")

        # this uses our custom AuthenticationBackend
        user = authenticate(request, username=username, password=password)

        login(request, user)

        # TODO: send SSE event: list of active users

        # TODO: de-duplicate session / user model search code

        # session_model = apps.get_model("sessions", "Session")
        # user_model = get_user_model()

        # active_sessions = session_model.objects.filter(
        #     expire_date__gt=timezone.now()
        # ).iterator()

        # active_user_ids = []
        # for session in active_sessions:
        #     session_data = session.get_decoded()
        #     user_id: str = session_data.get("_auth_user_id")
        #     if user_id:
        #         active_user_ids.append(user_id)

        # users = user_model.objects.filter(id__in=active_user_ids)
        # print([(user.first_name, user.last_name) for user in users])

    def logout(self, request: Request) -> None:

        self.verify_request_is_allowed(request)

        logout(request)

        # TODO: send SSE event: list of active users

    # TODO: better name: authenticate_request()
    def verify_request_is_allowed(self, request: Request) -> None:
        # TODO: Update this comment
        # user will be None unless logged in. Per default we use a
        # database-backed session management. The session data is
        # stored server-side and referenced by the session-id.
        # https://docs.djangoproject.com/en/5.2/topics/http/sessions/

        if not request.user.is_authenticated:
            raise BackendError(
                message="A request has been made by a user who is not signed in.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                user_message="Authentication failed. Are you signed in?",
            )

        # We validate the origin of the request. _validate_request_origin()
        # will throw an exception if anything is wrong.
        self._validate_request_origin(request)

        # extend the session
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)

    def verify_user_is_logged_in(self, user: User) -> None:

        # TODO: this is not possible as we do not have the request object
        # might be possible with custom middleware ???
        # not high priority as header data can be faked as well
        # self._validate_request_origin(request)

        if user is None:
            return False

        session_model = apps.get_model("sessions", "Session")

        non_expired_sessions = session_model.objects.filter(
            expire_date__gt=timezone.now()
        )
        for session in non_expired_sessions:
            data = session.get_decoded()
            if str(user.id) == str(data.get("_auth_user_id")):
                return True

        return False

        # TODO: comment: only extend the session on non-SSE request

    def _validate_request_origin(self, request: Request) -> None:
        # Check that the values from the start of the session match
        # with the values of this request.
        try:
            # This data has been set on login and will be checked when verifying
            # the request origin.
            headers = [
                "HTTP_USER_AGENT",
                "HTTP_ACCEPT_LANGUAGE",
                "REMOTE_ADDR",
            ]

            # Compare request header to origin of login.
            for header in headers:
                if request.session[header] != request.META.get(header):
                    raise BackendError(
                        message=f"Request origin mismatch, {header} did not match.",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        user_message="Authentication failed. Are you signed in?",
                    )

        # TODO: the comment does not match the error message ?!
        # KeyError occurs when the request is missing necessary data for
        # verification.
        except KeyError as e:
            raise BackendError(
                message="Incomplete or missing headers in request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e
