
import json
from pathlib import Path
from django.middleware.csrf import get_token
from django.apps import apps
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import jsonschema
import yaml
from .apps import InternalApp   # for type hints



# input validation:
# - use schema: https://pypi.org/project/jsonschema/
# - verify range of numbers
# - verify string length
# - regex patterns in strings
#     - allow only certain characters
#     - avoid: https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS
#     - use: https://owasp.org/www-community/OWASP_Validation_Regex_Repository

class RequestManager:

    def __init__(self) -> None:
        self.my_internal_app: InternalApp = apps.get_app_config('shelly_dirigent')
        
        # TODO: combine schemas for validation with those for documentation
        openapi_rel_path : str = './openapi.yaml'

        openapi_abs_path = Path(__file__).parent.parent.parent / openapi_rel_path

        with open(openapi_abs_path, 'r', encoding='utf8') as file:
            self.openapi = yaml.safe_load(file)

        pass


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
        # TODO: validate input
        schema = self.openapi['paths']['/api/switch']['post']['requestBody']['content']['application/json']['schema']
        jsonschema.validate(instance=request.data, schema=schema)

        self.my_internal_app.switch(request.data['id'], request.data['isOn'])
        # TODO: return proper response for all cases (also failure)
        return Response(None, status=status.HTTP_200_OK)