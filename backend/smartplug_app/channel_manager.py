from django_eventstream.channelmanager import DefaultChannelManager
from .login_manager import SessionManager

# source: https://pypi.org/project/django-eventstream/


class ChannelManager(DefaultChannelManager):

    def can_read_channel(self, user, channel):

        login_manager: SessionManager = SessionManager()

        return login_manager.authenticate_user(user)
