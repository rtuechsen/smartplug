from rest_framework.request import Request
from django.conf import settings
import asyncio
from .error_handler import BackendError
from rest_framework import status

_ERROR_CREDENTIAL_MISMATCH: str = "User credentials do not match."
_ERROR_BAD_REQUEST: str         = "There is an issue with the request."

# simulates LDAP-Process
# TODO: Implement LDAP
# This function may have latency as it connects to another server.
# Just in case it does, it is async for now
# TODO: Verify that async is necessary
async def authenticate(username: str, password: str) -> bool:
    await asyncio.sleep(2)
    if username == 'user' and password == 'pass':
        return True
    else:
        raise BackendError(message=_ERROR_CREDENTIAL_MISMATCH, status_code=status.HTTP_401_UNAUTHORIZED, user_message="TEST")

def _validate_request_origin(request: Request) -> bool:
    # Check that the values from the start of the session match
    # with the values of this request.
    try:
        user_agent = request.session['HTTP_USER_AGENT']
        accept_language = request.session['HTTP_ACCEPT_LANGUAGE']
        ip_address = request.session['REMOTE_ADDR']
        
        if all([
            user_agent == request.META.get('HTTP_USER_AGENT'),
            accept_language == request.META.get('HTTP_ACCEPT_LANGUAGE'),
            ip_address == request.META.get('REMOTE_ADDR'),
        ]):
            return True
        else:
            raise BackendError(message=_ERROR_CREDENTIAL_MISMATCH, status_code=status.HTTP_401_UNAUTHORIZED, user_message="TEST")
    # KeyError occurs when the request is missing necessary data for
    # verification.
    except KeyError:
        raise BackendError(message=_ERROR_BAD_REQUEST, status_code=status.HTTP_400_BAD_REQUEST, user_message="TEST")


class LoginManager:
    def __init__(self):
        pass

        # TODO: Integrate LDAP into login logic
        # TODO: Throw exception on login fail
    async def login(self, request: Request) -> bool:
        username: str = None
        password: str = None
        try:
            username = request.data.get('username')
            password = request.data.get('password')
        except KeyError:
            raise BackendError(message=_ERROR_BAD_REQUEST, status_code=status.HTTP_400_BAD_REQUEST, user_message="TEST")

        
        is_verified = await authenticate(username=username, password=password)
        if is_verified:
            request.session['USERNAME'] = username
            request.session['HTTP_USER_AGENT'] = request.META['HTTP_USER_AGENT']
            request.session['HTTP_ACCEPT_LANGUAGE'] = request.META['HTTP_ACCEPT_LANGUAGE']
            request.session['REMOTE_ADDR'] = request.META['REMOTE_ADDR']
            return True
        else:
            raise BackendError(message=_ERROR_CREDENTIAL_MISMATCH, status_code=status.HTTP_401_UNAUTHORIZED, user_message="TEST")

    def logout(self, request: Request):
        # Flushing the session will delete it and protects
        # from session fixation:
        # https://docs.djangoproject.com/en/5.2/topics/http/sessions/
        request.session.flush()

    # TODO: Throw exception on insufficient permission
    def get_user_permission(self, request: Request) -> bool:
        # user will be null unless logged in. Per default we use a 
        # database-backed session management. The session data is
        # stored server-side and referenced by the session-id.
        # https://stackoverflow.com/questions/5113421/what-is-the-difference-between-a-cookie-and-a-session-in-django
        # https://docs.djangoproject.com/en/5.2/topics/http/sessions/
        
        # We validate the origin of the request. _validate_request_origin()
        # will throw an exception if anything is wrong.
        if _validate_request_origin(request):
            try:
                user = request.session.get('USERNAME')
            except KeyError:
                raise BackendError(message=_ERROR_BAD_REQUEST, status_code=status.HTTP_400_BAD_REQUEST, user_message="TEST")

            if user:
                # If there is a user and the user needs permission, it means an action happened.
                # We therefor reset the expiry using the value in our settings.
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                return True