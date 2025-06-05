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


class RequestManager:
    """This class handles the incoming requests from the REST API.

    It delegates work to the backend and construct responses for the requests.
    """

    def __init__(self):
        """Constructor for the class."""

        ## The logger instance (singleton) used to log events and errors.
        self._logger: Logger = Logger()

        ## The SessionManager instance (singleton) used to authenticate
        ## requests.
        self._session_manager = SessionManager()

        ## An instance of ErrorHandler to simultaneously log an error and
        ## generate a response for the REST API.
        self._error_handler: ErrorHandler = ErrorHandler()

        ## The instance of SmartplugApp that manages the device tree.
        self.smartplug_app: SmartplugApp = apps.get_app_config("smartplug_app")

        # Because openapi.yaml already contains schemas for the requests for
        # documentation purposes, we extract those schemas and use them for
        # validation.
        openapi_rel_path: str = "./openapi.yaml"
        openapi_abs_path: Path = (
            Path(__file__).parent.parent.parent / openapi_rel_path
        )

        try:
            with open(openapi_abs_path, "r", encoding="UTF-8") as file:
                self._openapi: dict = yaml.safe_load(file)
        except FileNotFoundError as e:
            raise BackendError(
                f"Could not find the file openapi.yaml at {openapi_abs_path}."
            ) from e
        except IOError as e:
            raise BackendError(
                f"Error while reading the file openapi.yaml at "
                f"{openapi_abs_path}."
            ) from e
        except yaml.YAMLError as e:
            raise BackendError(f"Error while parsing openapi.yaml:{e}.") from e

        ## The OpenAPI schema for switch requests. Used to vaidate incoming
        ## requests.
        self._schema_switch: dict = self._openapi["paths"]["/api/switch"][
            "post"
        ]["requestBody"]["content"]["application/json"]["schema"]

        ## The OpenAPI schema for login requests. Used to vaidate incoming
        ## requests.
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

        # The body of this request should be empty.
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
        """Function to process requests to /login .

        @param request The incoming request.

        @return A response indication the success of the request.
        """

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
        """Function to process requests to /logout .

        @param request The incoming request.

        @return A response indication the success of the request.
        """

        # Note: the username would not be available by the time the event is
        # logged, as the session is invalidated. So we create a copy here.
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

        # The body of this request should be empty.
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

    def get_tree(self, request: Request) -> Response:
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

        # The body of this request should be empty.
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

        # The body of this request should be empty.
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

    def get_session_expiry_date(self, request: Request) -> Response:
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

        # The body of this request should be empty.
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

        try:
            self._session_manager.verify_request_is_allowed(request)
            session_expiry_date = (
                self._session_manager.get_session_expiry_date(request)
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
            {"session_expiry_date": session_expiry_date},
            status=status.HTTP_200_OK,
        )
