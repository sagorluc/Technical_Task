from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from common import ValidationError


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password"]
        
    def validate(self, attrs):
        password = attrs.get("password")
        conf_password = attrs.get("confirm_password")
        
        if not attrs.get("email"):
            raise ValidationError("Email are required")
        
        user = User.objects.filter(email=attrs["email"])
        
        if user.exists():
            raise ValidationError(f"{user.email} This email already exists.")
        
        if password != conf_password:
            raise ValidationError("Password does not match with confirmed password")
        
        return super().validate(attrs)

    def create(self, validated_data):
        role = self.context.get("role")
        is_staff = True if role == "admin" else False
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
            is_staff=is_staff,
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise ValidationError("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
        }
