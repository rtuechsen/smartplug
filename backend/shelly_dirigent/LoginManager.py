from django.middleware.csrf import get_token
from django.apps import apps
from rest_framework.request import Request

def VerifyLogin(username: str, password: str) -> bool:
    if username == 'user' and password == 'pass':
        return True
    else:
        return False

class RequestManager:
    """
    The request manager covers login requests
    and permission checks.
    """
    
    def login(username: str, password: str) -> bool:
        return True if VerifyLogin(username=username, password=password) else False

    def get_user_permission(request: Request) -> bool:
        # user will be null unless logged in. Per default we use a 
        # database-backed session management. The session data is
        # stored server-side and referenced by the session-id.
        # https://stackoverflow.com/questions/5113421/what-is-the-difference-between-a-cookie-and-a-session-in-django
        # https://docs.djangoproject.com/en/5.2/topics/http/sessions/
        user = request.session.get('username')
        if user:
            return True
        else:
            return False