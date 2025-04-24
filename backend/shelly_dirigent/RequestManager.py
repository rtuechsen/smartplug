from pathlib import Path
from django.middleware.csrf import get_token
from django.apps import apps
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import jsonschema
import yaml
from .apps import InternalApp  # for type hints only
from .Logger import Logger


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

        self.logger = Logger()

        # get the instance of InternalApp
        self.my_internal_app: InternalApp = apps.get_app_config("shelly_dirigent")

        # Because openapi.yaml already contains schemas for the requests for documentation purposes, we extract those schemas and use them for validation
        openapi_rel_path: str = "./openapi.yaml"

        openapi_abs_path = Path(__file__).parent.parent.parent / openapi_rel_path

        with open(openapi_abs_path, "r", encoding="utf8") as file:
            self.openapi = yaml.safe_load(file)

        self.schema_switch = self.openapi["paths"]["/api/switch"]["post"][
            "requestBody"
        ]["content"]["application/json"]["schema"]

        # TODO: handle file errors

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
        try:
            # get the schema for this endpoints request and validate the request with it
            jsonschema.validate(instance=request.data, schema=self.schema_switch)

            # instruct the app to perform the switch
            self.my_internal_app.switch(request.data["id"], request.data["isOn"])

            response = Response(None, status=status.HTTP_200_OK)

        except Exception as e:

            if hasattr(e, 'message'):
                self.logger.log(e.message)
            else:
                self.logger.log(str(e))

        # TODO: make sure to return proper response for all cases (also failures)
        return response
