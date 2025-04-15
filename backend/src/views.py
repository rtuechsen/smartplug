
from django.http import JsonResponse
from django.middleware.csrf import get_token

def csrf(request):
    """
    Generates a CSRF token.

    Args:
        request : The request for the CSRF token.

    Returns:
        JSON: The CSRF token.
    """
    return JsonResponse({'csrfToken': get_token(request)})

def ping(request):
    return JsonResponse({'result': 'Worked!'})

def login(request):
    return JsonResponse({'response': 1})