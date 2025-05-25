"""Contains the RequestManager that handles incoming requests from the REST
API."""

import copy
from pathlib import Path
from django.apps import apps
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import jsonschema
import yaml
from .apps import SmartplugApp
from .logger import Logger
from .error_handler import ErrorHandler, BackendError
from .session_manager import SessionManager

# TODO: verify that having multiple instances of the session manager does not
# lead to problems (when serving multiple users in multiple threads)


# rules for input validation (OWASP):
# - use schema: https://pypi.org/project/jsonschema/
# - verify range of numbers
# - verify string length
# - regex patterns in strings
#     - allow only certain characters
#     - avoid: https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS
#     - use: https://owasp.org/www-community/OWASP_Validation_Regex_Repository

# TODO: make RequestManager a singleton like Logger


class RequestManager:
    """This class handles the incoming requests from the REST API.

    It delegates work to the backend and construct responses for the
    requests.
    """

    def __init__(self):
        """Constructor for the class."""

        ## The logger instance (singleton) to log events and errors.
        self._logger: Logger = Logger()

        self._session_manager = SessionManager()

        ## An instance of ErrorHandler to simultaneously log an error and
        ## generate a response for the REST API.
        self._error_handler: ErrorHandler = ErrorHandler()

        ## The instance of TODO that manages the device tree.
        self.smartplug_app: SmartplugApp = apps.get_app_config("smartplug_app")

        # Because openapi.yaml already contains schemas for the requests for
        # documentation purposes, we extract those schemas and use them for
        # validation
        openapi_rel_path: str = "./openapi.yaml"
        openapi_abs_path: Path = (
            Path(__file__).parent.parent.parent / openapi_rel_path
        )

        with open(openapi_abs_path, "r", encoding="UTF-8") as file:
            self._openapi: dict = yaml.safe_load(file)
            # TODO: handle errors

        self._schema_switch: dict = self._openapi["paths"]["/api/switch"][
            "post"
        ]["requestBody"]["content"]["application/json"]["schema"]

        self._schema_login: dict = self._openapi["paths"]["/api/login"][
            "post"
        ]["requestBody"]["content"]["application/json"]["schema"]

    def csrf(self, request: Request) -> Response:
        """Function to process requests to /csrf .

        @param request The incoming request.

        @return A response containing either the CSRF token or an error.
        """

        self._logger.info(
            "A /csrf request has been received.",
            request.META["REMOTE_ADDR"],
            (
                request.session["USERNAME"]
                if "USERNAME" in request.session
                else None
            ),
        )

        if request.body != b"":
            return self._error_handler.response(
                "Requests to /csrf are not allowed to have a body.",
                status.HTTP_400_BAD_REQUEST,
                "The request did not match the expected schema.",
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        return Response(status=status.HTTP_200_OK)

    def login(self, request: Request) -> Response:
        """TODO."""

        self._logger.info(
            "A /login request has been received.",
            request.META["REMOTE_ADDR"],
            (
                request.session["USERNAME"]
                if "USERNAME" in request.session
                else None
            ),
        )

        try:
            jsonschema.validate(
                instance=request.data, schema=self._schema_login
            )
        except jsonschema.exceptions.ValidationError as e:
            return self._error_handler.response(
                f"The request did not match the expected schema: {e.message}",
                status.HTTP_400_BAD_REQUEST,
                "The request did not match the expected schema.",
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        try:
            self._session_manager.login(request)
        except BackendError as e:
            return self._error_handler.response(
                e.message,
                e.status_code,
                e.user_message,
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        return Response(None, status=status.HTTP_200_OK)

    def logout(self, request: Request) -> Response:
        """TODO."""

        # TODO: note, username would not be available by the time the event is
        # logged
        username = copy.copy(
            request.session["USERNAME"]
            if "USERNAME" in request.session
            else None
        )
        self._logger.info(
            "A /logout request has been received.",
            request.META["REMOTE_ADDR"],
            username,
        )

        if request.body != b"":
            return self._error_handler.response(
                "Requests to /logout are not allowed to have a body.",
                status.HTTP_400_BAD_REQUEST,
                "The request did not match the expected schema.",
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        try:
            self._session_manager.logout(request)
        except BackendError as e:
            return self._error_handler.response(
                e.message,
                e.status_code,
                e.user_message,
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        return Response(None, status=status.HTTP_200_OK)

    def gettree(self, request: Request) -> Response:
        """Function to process requests to /gettree .

        @param request The incoming request.

        @return A response containing either the device tree as a JSON or an
        error.
        """

        self._logger.info(
            "A /gettree request has been received.",
            request.META["REMOTE_ADDR"],
            (
                request.session["USERNAME"]
                if "USERNAME" in request.session
                else None
            ),
        )

        if request.body != b"":
            return self._error_handler.response(
                "Requests to /gettree are not allowed to have a body.",
                status.HTTP_400_BAD_REQUEST,
                "The request did not match the expected schema.",
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        try:
            self._session_manager.verify_request_is_allowed(request)

            device_tree = self.smartplug_app.get_device_tree_dicts()
        except BackendError as e:
            return self._error_handler.response(
                e.message,
                e.status_code,
                e.user_message,
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        return Response(device_tree, status=status.HTTP_200_OK)

    def switch(self, request: Request) -> Response:
        """Function to process requests to /switch .

        @param request The incoming request.

        @return A response containing either a success status or an error.
        """

        self._logger.info(
            "A /switch request has been received.",
            request.META["REMOTE_ADDR"],
            (
                request.session["USERNAME"]
                if "USERNAME" in request.session
                else None
            ),
        )

        try:
            jsonschema.validate(
                instance=request.data, schema=self._schema_switch
            )
        except jsonschema.exceptions.ValidationError as e:
            return self._error_handler.response(
                f"The request did not match the expected schema: {e.message}",
                status.HTTP_400_BAD_REQUEST,
                "The request did not match the expected schema.",
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        try:
            self._session_manager.verify_request_is_allowed(request)

            # instruct the app to perform the switch
            self.smartplug_app.switch(
                request.data["id"], request.data["desired_isOn"]
            )
        except BackendError as e:
            return self._error_handler.response(
                e.message,
                e.status_code,
                e.user_message,
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        return Response(None, status=status.HTTP_200_OK)

    def get_active_users(self, request: Request) -> Response:
        """Function to process requests to /getusers .

        @param request The incoming request.

        @return A response containing either the user list as a JSON or an error.
        """

        self._logger.info(
            "A /getusers request has been received.",
            request.META["REMOTE_ADDR"],
            (
                request.session["USERNAME"]
                if "USERNAME" in request.session
                else None
            ),
        )

        if request.body != b"":
            return self._error_handler.response(
                "Requests to /getactiveusers are not allowed to have a body.",
                status.HTTP_400_BAD_REQUEST,
                "The request did not match the expected schema.",
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        try:
            self._session_manager.verify_request_is_allowed(request)
            active_user_names = self._session_manager.get_active_user_names()
        except BackendError as e:
            return self._error_handler.response(
                e.message,
                e.status_code,
                e.user_message,
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        return Response(active_user_names, status=status.HTTP_200_OK)

    def get_remaining_session_time(self, request: Request) -> Response:
        """TODO"""

        self._logger.info(
            "A /getusers request has been received.",
            request.META["REMOTE_ADDR"],
            (
                request.session["USERNAME"]
                if "USERNAME" in request.session
                else None
            ),
        )

        if request.body != b"":
            return self._error_handler.response(
                "Requests to /getremainingsessiontime are not allowed to have "
                "a body.",
                status.HTTP_400_BAD_REQUEST,
                "The request did not match the expected schema.",
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        # Note: no authentication required, used from clients to determine if
        # they are still signed in

        try:
            remaining_session_time = (
                self._session_manager.get_remaining_session_time(request)
            )
        except BackendError as e:
            return self._error_handler.response(
                e.message,
                e.status_code,
                e.user_message,
                request.META["REMOTE_ADDR"],
                (
                    request.session["USERNAME"]
                    if "USERNAME" in request.session
                    else None
                ),
            )

        return Response(
            {"remaining_session_time": remaining_session_time},
            status=status.HTTP_200_OK,
        )
