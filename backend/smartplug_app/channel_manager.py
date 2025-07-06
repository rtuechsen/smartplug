"""Contains a ChannelManager that is used to authenticate SSE requests."""

from django_eventstream.channelmanager import DefaultChannelManager
from .session_manager import SessionManager

# source: https://pypi.org/project/django-eventstream/


class ChannelManager(DefaultChannelManager):
    """A channel manager used to authenticate SSE requests.

    Because SSE requests do not trigger a certain request handler as normal
    requests do, we need to define this additional layer for SSE and register
    it in the settings.
    """

    def __init__(self):
        """Contructor of the class, creates an instance of the SessionManager
        used to authenticate users.
        """

        ## The SessionManager instance (singleton) used to authenticate
        ## requests.
        self._session_manager: SessionManager = SessionManager()

    def can_read_channel(self, user, channel) -> bool:
        """Function to verify if a given user can read a given channel.

        This function is inherited from BaseBackend and required to be
        implemented.

        This primarily checks if the given user is logged in.

        @param user The user wo made the SSE request.

        @param channel The channel the user is trying to read.

        @return Boolean indicating if the user is allowed to read the channel
        (True) or not (False).
        """
        return self._session_manager.verify_user_is_logged_in(user)
