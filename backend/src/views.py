
from django.http import JsonResponse
from django.middleware.csrf import get_token

# tutorial: https://fractalideas.com/blog/making-react-and-django-play-well-together-single-page-app-model/

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def ping(request):
    return JsonResponse({'result': 'Worked!'})
