
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .RequestManager import RequestManager


request_manager = RequestManager()

# TODO: remove test endpoint
@api_view(["POST", "GET"])  # Ping is being called with both methods.
def ping(request):
    return Response({"result": "worked!"}, status=status.HTTP_200_OK)



@api_view(["GET"])
def csrf(request):
    return request_manager.csrf(request)


@api_view(["POST"])
def login(request):
    return request_manager.login(request)


@api_view(["POST"])
def logout(request):
    return request_manager.logout(request)


@api_view(["GET"])
def gettree(request):
    return request_manager.gettree(request)


@api_view(["POST"])
def switch(request):
    return request_manager.switch(request)



