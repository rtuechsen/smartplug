"""Contains the callbacks for the endpoints of the backend.

Django requires the endpoints to be defined in this file on file level.
In order to combine the handling of the endpoints in a class we forward
all requests to an instance of RequestManager.
"""

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from .request_manager import RequestManager

## The instance of the RequestManager. All requests are forwared to it.
request_manager = RequestManager()


@api_view(["GET"])
def csrf(request: Request) -> Response:
    """Callback for the /csrf endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.csrf(request)


@api_view(["POST"])
def login(request: Request) -> Response:
    """Callback for the /login endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.login(request)


@api_view(["POST"])
def logout(request: Request) -> Response:
    """Callback for the /logout endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.logout(request)


@api_view(["GET"])
def gettree(request: Request) -> Response:
    """Callback for the /gettree endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.gettree(request)


@api_view(["POST"])
def switch(request: Request) -> Response:
    """Callback for the /switch endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.switch(request)
