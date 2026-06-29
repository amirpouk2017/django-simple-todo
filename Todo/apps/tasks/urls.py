# from django.urls import path

# from .views import (
#     TaskListCreateView,
#     TaskRetrieveUpdateDestroyView,
# )

# urlpatterns = [
#     path(
#         "",
#         TaskListCreateView.as_view(),
#         name="task-list-create",
#     ),
#     path(
#         "<uuid:pk>/",
#         TaskRetrieveUpdateDestroyView.as_view(),
#         name="task-detail",
#     ),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("task", views.TaskView, basename="tasks")
urlpatterns = [path("", include(router.urls))]
