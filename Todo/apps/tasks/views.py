from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Task


class TaskPagination(PageNumberPagination):
    page_size = 10


class TaskView(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    search_fields = ["title", "description"]

    filterset_fields = [
        "priority",
        "is_complete",
    ]
    ordering_fields = [
        "created",
        "due",
        "priority",
    ]
