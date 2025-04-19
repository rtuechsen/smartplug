
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework import status

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