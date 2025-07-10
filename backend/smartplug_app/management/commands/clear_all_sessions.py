from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session

class Command(BaseCommand):
    help = "Delete all session records"

    def handle(self, *args, **options):
        Session.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Deleted all sessions"))