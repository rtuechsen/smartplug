
from django.apps import AppConfig
import threading
import time
from django_eventstream import send_event


class InternalApp(AppConfig):
    name = "shelly_dirigent"
    background_task_started = False
    
    def ready(self):
        print("\n\n -> Starting internal app ...\n\n")
        
        if not self.background_task_started:
            self.background_task_started = True
            thread = threading.Thread(target=self.loop, daemon=True)
            thread.start()


    def loop(self):
        while True:
            print('\n\n -> Running background task ...\n\n')
            send_event("labor_config", "message", {"text": "hello world"})
            time.sleep(5)
