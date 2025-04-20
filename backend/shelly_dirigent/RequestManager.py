
import json
from pathlib import Path
from django.middleware.csrf import get_token
from django.apps import apps
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import jsonschema
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
        SCHEMAS_FILE_PATH : str = './schemas.json'

        schemas_path = Path(__file__).parent / SCHEMAS_FILE_PATH

        try:
            with open(schemas_path, 'r', encoding='utf8') as file:
                schemas_json_string = file.read()
        except FileNotFoundError:
            print(f'Error: Could not find the file {schemas_path}')
        except IOError:
            print(f'Error: while reading the file {schemas_path}')

        try:
            self.schemas = json.loads(schemas_json_string)
        except ValueError as e:
            print(f'Error: Could not parse JSON {schemas_json_string} because {e}')


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
        schema = self.schemas['switch']
        jsonschema.validate(instance=request.data, schema=schema)

        self.my_internal_app.switch(request.data['id'], request.data['isOn'])
        # TODO: return proper response for all cases (also failure)
        return Response(None, status=status.HTTP_200_OK)