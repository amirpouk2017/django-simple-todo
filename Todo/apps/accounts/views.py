from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from time import time
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed

from config.redis import REDIS_CLIENT
from .serializers import UserSerializer, AuthSerializer
from django.conf import settings
from config.settings import EnvironmentEnum
from config.logger import log

logger = log
REFRESH_TOKEN_LIFETIME = settings.REFRESH_TOKEN_LIFETIME
IS_PROD = True if settings.ENV == EnvironmentEnum.PROD else False
User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request=request,
            **serializer.validated_data,
        )
        if user is None:
            raise AuthenticationFailed("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        response = Response(
            {"access": str(access)},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SESSION_COOKIE_SAMESITE,
            path="/",
        )
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        access_token = request.auth
        ttl = max(0, int(access_token["exp"] - time()))
        REDIS_CLIENT.setex(
            f"bl:access:{access_token['jti']}",
            ttl,
            "1",
        )
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        response = Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie(
            key="refresh_token",
            path="/",
        )
        return response


class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    permission_classes = [AllowAny]

    authentication_classes = []

    def post(self, request):

        raw_refresh = request.COOKIES.get("refresh_token")

        if not raw_refresh:
            raise AuthenticationFailed("Refresh token missing")

        try:
            old_refresh = RefreshToken(raw_refresh)
        except TokenError:
            raise AuthenticationFailed("Invalid refresh token")

        user_id = old_refresh.get("user_id")

        user = User.objects.get(pk=user_id)

        old_refresh.blacklist()

        new_refresh = RefreshToken.for_user(user)

        access = new_refresh.access_token

        response = Response({"access": str(access)}, status=200)

        response.set_cookie(
            key="refresh_token",
            value=str(new_refresh),
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SESSION_COOKIE_SAMESITE,
            path="/",
        )

        return response
