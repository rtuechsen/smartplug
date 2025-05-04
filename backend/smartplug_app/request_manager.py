"""Contains the RequestManager that handles incoming requests from the REST
API."""

from pathlib import Path
from django.middleware.csrf import get_token
from django.apps import apps
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import jsonschema
import yaml
from .apps import SmartplugApp
from .logger import Logger
from .error_handler import ErrorHandler, BackendError


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

        ## An instance of ErrorHandler to simultaneously log an error and generate a response for the REST API.
        self._error_handler: ErrorHandler = ErrorHandler()

        ## The instance of TODO that manages the device tree.
        self.smartplug_app: SmartplugApp = apps.get_app_config("smartplug_app")

        # Because openapi.yaml already contains schemas for the requests for documentation purposes, we extract those schemas and use them for validation
        openapi_rel_path: str = "./openapi.yaml"
        openapi_abs_path: Path = Path(__file__).parent.parent.parent / openapi_rel_path

        with open(openapi_abs_path, "r", encoding="UTF-8") as file:
            self._openapi: dict = yaml.safe_load(file)
            # TODO: handle errors

        self._schema_switch: dict = self._openapi["paths"]["/api/switch"]["post"][
            "requestBody"
        ]["content"]["application/json"]["schema"]

    def csrf(self, request: Request) -> Response:
        """Function to process requests to /csrf .

        @param request The incoming request.

        @return A response containing either the CSRF token or an error.
        """
        # TODO: add more info to log: WHO has send that request? ip, user name, ...
        self._logger.info("A /csrf request has been received.")

        return Response({"csrfToken": get_token(request)}, status=status.HTTP_200_OK)

    def login(self, request: Request) -> Response:
        return Response(None, status=status.HTTP_200_OK)

    def logout(self, request: Request) -> Response:
        return Response(None, status=status.HTTP_200_OK)

    def gettree(self, _: Request) -> Response:
        """Function to process requests to /gettree .

        @param request The incoming request.

        @return A response containing either the device tree as a JSON or an error.
        """
        # No schema validation needed here a there is no payload expected in the request. Any payload in the request would be ignored.

        # TODO: add more info to log: WHO has send that request? ip, user name, ...
        self._logger.info("A /gettree request has been received.")
        # TODO: handle errors
        device_tree = self.smartplug_app.get_device_tree_dicts()
        return Response(device_tree, status=status.HTTP_200_OK)

    def switch(self, request: Request) -> Response:
        """Function to process requests to /switch .

        @param request The incoming request.

        @return A response containing either a successn status or an error.
        """
        # TODO: log request: WHO requested WHAT - wait for session management to identify user ???
        self._logger.info("A /switch request has been received.")

        try:
            jsonschema.validate(instance=request.data, schema=self._schema_switch)
        except jsonschema.exceptions.ValidationError as e:
            return self._error_handler.response(
                e.message,
                status.HTTP_400_BAD_REQUEST,
                "The request did not match the expected schema.",
            )

        try:
            # instruct the app to perform the switch
            self.smartplug_app.switch(request.data["id"], request.data["isOn"])
        except BackendError as e:
            return self._error_handler.response(
                e.message, e.status_code, e.user_message
            )

        # TODO: make sure to return proper response for all cases (also failures)

        return Response(None, status=status.HTTP_200_OK)
