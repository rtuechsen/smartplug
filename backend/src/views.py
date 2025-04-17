from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view,
)  # We use @api_view to restrict REST methods
from .serverside_processes.session_manager import SessionManager

session_manager = SessionManager()


@api_view(["GET"])
def csrf(request):
    """
    Generates a CSRF token.

    Args:
        request : The request for the CSRF token.

    Returns:
        JSON: The CSRF token.
    """
    return Response({"csrfToken": get_token(request)}, status=status.HTTP_200_OK)


@api_view(["POST", "GET"])  # Ping is being called with both methods.
def ping(request):
    #
    Class.logic()
    #
    return Response({"result": "worked!"}, status=status.HTTP_200_OK)


# adadfafaf


# afafafawfa
