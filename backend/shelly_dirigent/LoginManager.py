from rest_framework.request import Request
from django.conf import settings
import asyncio

# simulates LDAP-Process
# TODO: Implement LDAP
# This function may have latency as it connects to another server.
# Just in case it does, it is async for now
# TODO: Verify that async is necessary
async def authenticate(username: str, password: str) -> bool:
    await asyncio.sleep(5)
    if username == 'user' and password == 'pass':
        return True
    else:
        return False

class LoginManager:
    def __init__(self):
        pass

        # TODO: Integrate LDAP into login logic
        # TODO: Throw exception on login fail
    async def login(self, username: str, password: str, request: Request) -> bool:
        is_verified = await authenticate(username=username, password=password)
        if is_verified:
            request.session['username'] = username
            return True
        else:
            return False

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
        user = request.session.get('username')
        if user:
            # If there is a user and the user needs permission, it means an action happened.
            # We therefor reset the expiry using the value in our settings.
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            return True
        else:
            return False