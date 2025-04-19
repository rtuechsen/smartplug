
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework import status

# input validation:
# - use schema: https://pypi.org/project/jsonschema/
# - verify range of numbers
# - verify string length
# - regex patterns in strings
#     - allow only certain characters
#     - avoid: https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS
#     - use: https://owasp.org/www-community/OWASP_Validation_Regex_Repository

class RequestManager:

    def csrf(self, request):
        return Response({"csrfToken": get_token(request)}, status=status.HTTP_200_OK)


    def login(self, request):
        return Response({}, status=status.HTTP_200_OK)


    def logout(self, request):
        return Response({}, status=status.HTTP_200_OK)


    def gettree(self, request):
        return Response({}, status=status.HTTP_200_OK)


    def switch(self, request):
        return Response({}, status=status.HTTP_200_OK)