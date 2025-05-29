"""Contains ... TODO.

TODO: more details ???
"""

import time
import threading
import datetime
from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.request import Request
import django_eventstream
from .error_handler import BackendError
from .logger import Logger


class SessionManager:

    _instance: "SessionManager" = None

    _invalidate_sessions_thread: threading.Thread

    _invalidate_sessions_thread_lock: threading.Lock = threading.Lock()

    _logger: Logger = Logger()

    def __new__(cls):
        """Creates an instance of the class.

        Implements the singleton pattern taken from this tutorial:
        https://python-patterns.guide/gang-of-four/singleton/
        """

        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)

            # We need to do the initializations here because __init__() would
            # be called every time an instance is requested.

            cls._invalidate_sessions_thread = threading.Thread(
                target=cls._invalidate_sessions, daemon=True
            )

        return cls._instance

    def _invalidate_sessions(self) -> None:

        while True:

            # check which sessions have expired
            session_model = apps.get_model("sessions", "Session")
            user_model = get_user_model()

            now: datetime.datetime = timezone.now()

            active_sessions = session_model.objects.filter(
                expire_date__gt=now
            ).iterator()

            expired_sessions = session_model.objects.filter(
                expire_date__lt=now
            ).iterator()

            expired_user_ids = []
            for session in expired_sessions:
                session_data = session.get_decoded()
                session.delete()
                user_id: str = session_data.get("_auth_user_id")
                if user_id:
                    expired_user_ids.append(user_id)

            # invalidate SSE for user
            users = user_model.objects.filter(id__in=expired_user_ids)
            for user in users:
                # TODO: this will send a response to the client with some JSON
                # data -> try to send own response to hide implementation details
                django_eventstream.channel_permission_changed(user, "default")
                # TODO: log IP address as well (stored in session)
                self._logger.info(
                    message="A user session expired.", username=user.username
                )

            # send updated user list (if there was a change)
            self._send_list_of_active_users()

            expiry_times: list[float] = [
                (session.expire_date - now).total_seconds()
                for session in active_sessions
            ]

            # if no open sessions: end thread
            if len(expiry_times) == 0:
                return

            time_to_next_expiry = min(expiry_times)

            # set sleep timer to the expiry time of the next open session
            # (+ some threshold to make sure session is really expired)
            EXPIRY_TIME_THRESHOLD: float = 0.01
            time.sleep(time_to_next_expiry + EXPIRY_TIME_THRESHOLD)

    def login(self, request: Request) -> None:

        username = request.data.get("username")
        password = request.data.get("password")

        # this uses our custom AuthenticationBackend
        user = authenticate(request, username=username, password=password)

        login(request, user)
        # need to save to database, otherwise user is not guarantied to be
        # available in following queries
        request.session.save()

        with SessionManager._invalidate_sessions_thread_lock:
            if not SessionManager._invalidate_sessions_thread.is_alive():
                SessionManager._invalidate_sessions_thread = threading.Thread(
                    target=self._invalidate_sessions, daemon=True
                )
                SessionManager._invalidate_sessions_thread.start()

        self._send_list_of_active_users()

    def logout(self, request: Request) -> None:

        self.verify_request_is_allowed(request)

        logout(request)
        # need to save to database, otherwise user is not guarantied to be
        # available in following queries
        request.session.save()

        self._send_list_of_active_users()

    def _send_list_of_active_users(self):

        django_eventstream.send_event(
            "default",
            "user_list_update",
            self.get_active_user_names(),
        )

    def get_active_user_names(self) -> list[str]:

        # TODO: turn these into class variables ???
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
            f"{user.first_name} {user.last_name}".strip()
            for user in active_users
        ]
        return acitve_user_names

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

    def get_remaining_session_time(self, request: Request) -> float:

        try:
            self.verify_request_is_allowed(request)
        except BackendError:
            return 0.0

        return (
            request.session.get_expiry_date() - timezone.now()
        ).total_seconds()
