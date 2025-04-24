# TODO: use correct fromat for python documentation: https://www.doxygen.nl/manual/docblocks.html#pythonblocks

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from .RequestManager import RequestManager

# The instance of the RequestManager of the API. All requests are forwarded to it.
# Django requires all functions for the API endpoints to be defined in this file at file level.
# So to combine the handling of requests in a class we have to forward each of them.
request_manager = RequestManager()


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
