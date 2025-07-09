"""Contains the logic for the SessionManager class. Authentication and
permission checks are done inside this class.
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
    """
    The SessionManager class is responsible for Authenticating users,
    checking permissions, extending session lifetime and signing out users
    manually. Automatic sign-outs are handled by Djangos internal session
    expiry and is configured in admin_settings.py.
    The SessionManager is a singleton.
    """

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
        """Function used to clean up expired or invalidated sessions. Meant to
        be run as a background task in a separate thread.
        """
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

                django_eventstream.channel_permission_changed(user, "default")
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
            # Note: sleep() is not needed for the program to work correctly, it
            # is only used reduce CPU utilization. If removed the program will
            # do 'busy waiting'.
            expiry_time_threshold: float = 0.01
            time.sleep(time_to_next_expiry + expiry_time_threshold)

    def login(self, request: Request) -> None:
        """Checks user credentials and signs the user in on matching
        credentials.

        @param request The user's request containing credentials.
        """

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
        """Logs out the user on request.

        @param request The user's request.
        """

        # Verify origin of the request to avoid false signouts or unintended
        # behaviour.
        self.verify_request_is_allowed(request)

        # This logout function implemented by django. This is not recursive.
        logout(request)

        # Update the active user list in the web page.
        self._send_list_of_active_users()

    def _send_list_of_active_users(self) -> None:
        """Broadcasts a list of signed in users using SSE."""

        django_eventstream.send_event(
            "default",
            "user_list_update",
            self.get_active_users_full_names(),
        )

    def get_active_users_full_names(self) -> list[str]:
        """Constructs a list of containing the full name of each user.
        Only users that are signed in will be included. Full names consist of
        first and last name.

        @return The list containing the names of all active users as string.
        """

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
        active_users_full_names = [
            f"{user.first_name} {user.last_name}".strip()
            for user in active_users
        ]
        return active_users_full_names

    def get_active_usernames(self) -> list[str]:
        """Constructs a list of containing the username of each user.
        Only users that are signed in will be included. The username is the
        identificator used on sign in.

        @return The list containing the usernames of all active users as string.
        """

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
        active_usernames = [user.username for user in active_users]
        return active_usernames

    def verify_request_is_allowed(self, request: Request) -> None:
        """Checks the incoming request for access permission. Also validates
        origin of request to prevent session theft. If the request is valid,
        the session timeout will be reset.

        @param request The request to be validated.
        """

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

    def verify_user_is_logged_in(self, user: User) -> bool:
        """Used to check if a session has expired.
        Unlike verify_request_is_allowed() it will not extend the session
        lifetime and only verifies this user currently exists.

        @param user The user object to be checked.

        @return True if the user exists and is logged in, otherwise False.
        """

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

    def _validate_request_origin(self, request: Request) -> None:
        """This function prevents session theft by comparing USER_AGENT,
        ACCEPT_LANGUAGE and REMOTE_ADDR from the first request made in a
        session to current values.

        @param request The request to be verified.
        """

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

        # KeyError occurs when the request is missing necessary data for
        # verification.
        except KeyError as e:
            raise BackendError(
                message="Incomplete or missing headers in request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    def get_session_expiry_date(self, request: Request) -> datetime.datetime:
        """Simple function to obtain the date of expiry from a session.

        @param request The request which the session is identified by
        """

        try:
            self.verify_request_is_allowed(request)
        except BackendError:
            return 0.0

        return request.session.get_expiry_date()
