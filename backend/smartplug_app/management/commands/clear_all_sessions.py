# Code source:
# https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session

class Command(BaseCommand):
    help = "Delete all sessions, including active ones."

    def handle(self, *args, **options):
        # Source:
        # https://docs.djangoproject.com/en/5.2/topics/auth/customizing/
        Session.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Deleted all sessions"))