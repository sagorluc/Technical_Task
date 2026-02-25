from .models import User, Profile
from rest_framework import generics, status
from .serializers import ProfileSerializer, SignUpSerializer, LoginSerializer
from rest_framework.permissions import AllowAny
from e_commerce.utils import AuthenticatedUser, Response


class UserSignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                return Response(
                    success=True,
                    message="User created successfully",
                    data=serializer.data,
                    status_code=status.HTTP_201_CREATED,
                )
            return Response(
                success=False,
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                return Response(
                    success=True,
                    message="User login successfully",
                    data=serializer.validated_data,
                    status_code=status.HTTP_200_OK,
                )
            return Response(
                success=False,
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AuthenticatedUser]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            profile = Profile.objects.filter(user=user).first()
            serializer = self.get_serializer(profile)
            return Response(
                success=True,
                message="Retrive user profile successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            profile = Profile.objects.filter(user=user).first()
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    success=True,
                    message="User profile updated",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK,
                )
            return Response(
                success=False,
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
