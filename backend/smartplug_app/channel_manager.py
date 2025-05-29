from django_eventstream.channelmanager import DefaultChannelManager
from .session_manager import SessionManager

# source: https://pypi.org/project/django-eventstream/


class ChannelManager(DefaultChannelManager):

    def __init__(self):
        self._login_manager: SessionManager = SessionManager()

    def can_read_channel(self, user, channel):
        return self._login_manager.verify_user_is_logged_in(user)
