from django.apps import AppConfig


class SrcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shelly_dirigent"

    def ready(self):
        print("SRC")
