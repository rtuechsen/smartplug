from typing import Any
from django.apps import apps

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
import django_eventstream


def send_event(channel: str, event_type: str, data: Any):

    # credit: https://stackoverflow.com/questions/61217689/how-do-i-get-all-current-sessions-from-django

    session_model = apps.get_model("sessions", "Session")

    expired_sessions = session_model.objects.filter(
        expire_date__lt=timezone.now()
    ).iterator()

    expired_user_ids = []
    for session in expired_sessions:
        session_data = session.get_decoded()
        session.delete()
        user_id: str = session_data.get("_auth_user_id")
        if user_id:
            expired_user_ids.append(user_id)

    user_model = get_user_model()

    users = user_model.objects.filter(id__in=expired_user_ids)
    for user in users:
        print("removed user:", user)
        django_eventstream.channel_permission_changed(user, channel)

    django_eventstream.send_event(channel, event_type, data)

    # TODO: remove, debug code
    # active_sessions = session_model.objects.filter(
    #     expire_date__gt=timezone.now()
    # ).iterator()

    # active_user_ids = []
    # for session in active_sessions:
    #     session_data = session.get_decoded()
    #     user_id: str = session_data.get("_auth_user_id")
    #     if user_id:
    #         active_user_ids.append(user_id)

    # print("event was sent to:")
    # users = user_model.objects.filter(id__in=active_user_ids)
    # for user in users:
    #     print("\t", user)
