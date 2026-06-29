# apps/tasks/services.py

from datetime import timedelta
from django.utils import timezone
from .tasks import send_task_reminder


def schedule_reminder(task):
    reminder_time = task.due - timedelta(hours=1)

    delay = (reminder_time - timezone.now()).total_seconds()

    if delay <= 0:
        return

    send_task_reminder.apply_async(
        args=[str(task.id)],
        countdown=int(delay),
    )
