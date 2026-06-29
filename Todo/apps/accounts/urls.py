from django.urls import path

from .views import RegisterView, LoginView, LogoutView, Me, RefreshView

urlpatterns = [
    path("signup/", RegisterView.as_view()),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", Me.as_view(), name="me"),
]
