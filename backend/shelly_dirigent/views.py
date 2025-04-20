
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view
from .RequestManager import RequestManager

# unfortunately it is not possible to receive all requests in class directly, thus we have to redirect them
# TODO: let django create request manager instance as an app?
request_manager = RequestManager()

# TODO: remove test endpoint
@api_view(["POST", "GET"])  # Ping is being called with both methods.
def ping(request):
    return Response({"result": "worked!"}, status=status.HTTP_200_OK)



@api_view(["GET"])
def csrf(request: Request) -> Response:
    return request_manager.csrf(request)


@api_view(["POST"])
def login(request: Request) -> Response:
    return request_manager.login(request)


@api_view(["POST"])
def logout(request: Request) -> Response:
    return request_manager.logout(request)


@api_view(["GET"])
def gettree(request: Request) -> Response:
    return request_manager.gettree(request)


@api_view(["POST"])
def switch(request: Request) -> Response:
    return request_manager.switch(request)



