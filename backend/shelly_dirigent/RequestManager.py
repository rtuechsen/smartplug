from pathlib import Path
from django.middleware.csrf import get_token
from django.apps import apps
import jsonschema.exceptions
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import exceptions as drf_exceptions
import jsonschema
import yaml
from .apps import InternalApp  # for type hints only


# input validation:
# - use schema: https://pypi.org/project/jsonschema/
# - verify range of numbers
# - verify string length
# - regex patterns in strings
#     - allow only certain characters
#     - avoid: https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS
#     - use: https://owasp.org/www-community/OWASP_Validation_Regex_Repository


class RequestManager:
    """This is an example docstring.

    Here are some details.
    """

    def __init__(self) -> None:
        # get the instance of InternalApp
        self.my_internal_app: InternalApp = apps.get_app_config("shelly_dirigent")

        # Because openapi.yaml already contains schemas for the requests for documentation purposes, we extract those schemas and use them for validation
        openapi_rel_path: str = "./openapi.yaml"

        openapi_abs_path = Path(__file__).parent.parent.parent / openapi_rel_path

        with open(openapi_abs_path, "r", encoding="utf8") as file:
            self.openapi = yaml.safe_load(file)

    def csrf(self, request: Request) -> Response:
        return Response({"csrfToken": get_token(request)}, status=status.HTTP_200_OK)

    def login(self, request: Request) -> Response:
        return Response(None, status=status.HTTP_200_OK)

    def logout(self, request: Request) -> Response:
        return Response(None, status=status.HTTP_200_OK)

    def gettree(self, request: Request) -> Response:
        device_tree = self.my_internal_app.get_device_tree_dicts()
        return Response(device_tree, status=status.HTTP_200_OK)

    def switch(self, request: Request) -> Response:
        """This is an example docstring.

        Here are some details.

        @param request This is some parameter.

        @return This is some return value.

        """
        # get the schema for this endpoints request and validate the request with it
        # TODO: dont retrieve schema every time
        schema = self.openapi["paths"]["/api/switch"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"]
        try:
            jsonschema.validate(instance=request.data, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            raise drf_exceptions.ValidationError(
                detail="Error: Request for /switch is illformed!"
            ) from e

        # instruct the app to perform the switch
        self.my_internal_app.switch(request.data["id"], request.data["isOn"])

        # TODO: make sure to return proper response for all cases (also failures)
        return Response(None, status=status.HTTP_200_OK)
