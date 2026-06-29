from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.filter(email=validated_data["email"])
        if user:
            raise serializers.ValidationError("User Already exist")

        if validated_data["password"] != validated_data["password2"]:
            raise serializers.ValidationError("Passwords does not match")

        del validated_data["password2"]

        return User.objects.create_user(**validated_data)


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
