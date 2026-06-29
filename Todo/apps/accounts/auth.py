from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from config.redis import REDIS_CLIENT


class RedisJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)

        jti = token.get("jti")
        if jti and REDIS_CLIENT.exists(f"bl:access:{jti}"):
            raise AuthenticationFailed("Access token has been revoked.")

        return token
