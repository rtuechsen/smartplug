from django_eventstream.channelmanager import DefaultChannelManager
from .login_manager import LoginManager

# source: https://pypi.org/project/django-eventstream/


class ChannelManager(DefaultChannelManager):

    def can_read_channel(self, user, channel):

        if user is None:
            return False

        login_manager: LoginManager = LoginManager()

        login_manager.authenticate_user(user)

        return True
