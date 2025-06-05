"""Contains the callbacks for the endpoints of the backend.

Django requires the endpoints to be defined in this file on file level.
In order to combine the handling of the endpoints in a class we forward
all requests to an instance of RequestManager.
"""

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from django.views.decorators.csrf import ensure_csrf_cookie
from .request_manager import RequestManager

# Django requires all functions for the API endpoints to be defined in this
# file at file level.
# So to combine the handling of requests in a class we have to forward each of
# them.
## The instance of the RequestManager. All requests are forwared to it.
request_manager = RequestManager()


@ensure_csrf_cookie
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
def get_tree(request: Request) -> Response:
    """Callback for the /gettree endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.get_tree(request)


@api_view(["POST"])
def switch(request: Request) -> Response:
    """Callback for the /switch endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.switch(request)


@api_view(["GET"])
def get_active_users(request: Request) -> Response:
    """Callback for the /getusers endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.get_active_users(request)


@api_view(["GET"])
def get_session_expiry_date(request: Request) -> Response:
    """Callback for the /get-session-expiry-date endpoint.

    @param request The request from the REST API.

    @return The response from the request manager for the REST API.
    """
    return request_manager.get_session_expiry_date(request)
