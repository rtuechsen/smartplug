

from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


# TODO: remove test endpoint
@api_view(["POST", "GET"])  # Ping is being called with both methods.
def ping(request):
    return Response({"result": "worked!"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def csrf(request):
    return Response({"csrfToken": get_token(request)}, status=status.HTTP_200_OK)


@api_view(["POST"])
def login(request):
    return Response({}, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response({}, status=status.HTTP_200_OK)


@api_view(["GET"])
def gettree(request):
    return Response({}, status=status.HTTP_200_OK)


@api_view(["POST"])
def switch(request):
    return Response({}, status=status.HTTP_200_OK)



