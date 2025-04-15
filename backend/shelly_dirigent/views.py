from django.http import JsonResponse
from django.middleware.csrf import get_token
#from rest_framework.response import Response
#from rest_framework.response import status

def csrf(request):
    """
    Generates a CSRF token.

    Args:
        request : The request for the CSRF token.

    Returns:
        JSON: The CSRF token.
    """
    return JsonResponse({'csrfToken': get_token(request)})
    #return Response({'csrfToken': get_token(request)}, status=status.HTTP_200_OK)

def ping(request):
    return JsonResponse({'result': 'Worked!'})
