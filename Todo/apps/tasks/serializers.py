from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Task

User = get_user_model()


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="tasks-detail")

    class Meta:
        model = Task
        fields = (
            "url",
            "id",
            "title",
            "description",
            "created",
            "due",
            "priority",
            "is_complete",
        )
        extra_kwargs = {
            "title": {
                "write_only": True,
            }
        }

    def create(self, validated_data):
        return Task.objects.create(**validated_data)
