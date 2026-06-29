import uuid
from django.db import models
from django.conf import settings


class Task(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 0, "Low"
        MEDIUM = 1, "Medium"
        HIGH = 2, "High"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(
        max_length=5000,
        blank=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    due = models.DateTimeField(
        null=True,
        blank=True,
    )
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    is_complete = models.BooleanField(
        default=False,
    )

    def __str__(self) -> str:
        return self.title
