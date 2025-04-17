
from django.apps import AppConfig

class InternalApp(AppConfig):
    name = "shelly_dirigent"

    def ready(self):
        print("\n\n -> Starting internal app ...\n\n")
