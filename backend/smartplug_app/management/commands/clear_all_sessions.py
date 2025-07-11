"""Contains a class that allows removing all existing sessions."""

from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session


class Command(BaseCommand):
    """
    This class is used to create a command for manage.py to delete all existing
    sessions. The command can be called like this:
    sudo -E env PATH="$PATH" python manage.py clear_all_sessions

    The code is based on:
    https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/
    """

    help = "Delete all sessions, including active ones."

    def handle(self, *args, **options):
        """Function that is called when using the command.

        @param args A number of additional arguments. Not used.

        @param options A number of additional options. Not used.
        """

        # Source: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/
        Session.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Deleted all sessions"))
