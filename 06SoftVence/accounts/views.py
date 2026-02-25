from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from common.validation_err import ValidationError
from .serializers import SignupSerializer, LoginSerializer
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from common import Response

class AdminSignupAPIView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=inline_serializer(
            name="SignupSerializer",
            fields={
                "email": drf_serializers.EmailField(
                    required=True,
                ),
                "password": drf_serializers.CharField(
                    required=True,
                ),
                "confirm_password": drf_serializers.CharField(
                    required=True,
                ),
            },
        ),
        responses={
            201: inline_serializer(
                name="AdminSignupAPIViewResponse",
                fields={
                    "success": drf_serializers.BooleanField(),
                    "message": drf_serializers.CharField(),
                },
            )
        },
    )
    def post(self, request):
        try:
            role = "admin"
            serializer = SignupSerializer(data=request.data, context={"role": role})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(message="Admin created", status_code=201)
        except ValidationError as e:
            return Response(
                success=False,
                message=e.detail["message"],
                status_code=e.detail["status_code"],
            )

class VendorSignupAPIView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=inline_serializer(
            name="SignupSerializer",
            fields={
                "email": drf_serializers.EmailField(
                    required=True,
                ),
                "password": drf_serializers.CharField(
                    required=True,
                ),
                "confirm_password": drf_serializers.CharField(
                    required=True,
                ),
            },
        ),
        responses={
            201: inline_serializer(
                name="VendorSignupAPIViewResponse",
                fields={
                    "success": drf_serializers.BooleanField(),
                    "message": drf_serializers.CharField(),
                },
            )
        },
    )
    def post(self, request):
        try:
            role = "vendor"
            serializer = SignupSerializer(data=request.data, context={"role": role})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(message="Vendor created", status_code=201)
        except ValidationError as e:
            return Response(
                success=False,
                message=e.detail["message"],
                status_code=e.detail["status_code"],
            )

    
class CustomerSignupAPIView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=inline_serializer(
            name="SignupSerializer",
            fields={
                "email": drf_serializers.EmailField(
                    required=True,
                ),
                "password": drf_serializers.CharField(
                    required=True,
                ),
                "confirm_password": drf_serializers.CharField(
                    required=True,
                ),
            },
        ),
        responses={
            201: inline_serializer(
                name="CustomerSignupAPIViewResponse",
                fields={
                    "success": drf_serializers.BooleanField(),
                    "message": drf_serializers.CharField(),
                },
            )
        },
    )
    def post(self, request):
        try:
            role = "customer"
            serializer = SignupSerializer(data=request.data, context={"role": role})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(message="Customer created", status_code=201)
        except ValidationError as e:
            return Response(
                success=False,
                message=e.detail["message"],
                status_code=e.detail["status_code"],
            )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer(
            name="LoginSerializer",
            fields={
                "email": drf_serializers.EmailField(
                    required=True,
                ),
                "password": drf_serializers.CharField(
                    required=True,
                ),
            },
        ),
        responses={
            201: inline_serializer(
                name="LoginAPIViewResponse",
                fields={
                    "success": drf_serializers.BooleanField(),
                    "access": drf_serializers.CharField(),
                    "refresh": drf_serializers.CharField(),
                    "role": drf_serializers.CharField(),
                },
            )
        },
    )
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(message="Login successfully", data=serializer.validated_data, status_code=200)
        except ValidationError as e:
            return Response(
                success=False,
                message=e.detail["message"],
                status_code=e.detail["status_code"],
            )
        except Exception as e:
            str_errors = str(e).strip("[]\"'")
            return Response(
                success=False,
                message=str_errors,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

