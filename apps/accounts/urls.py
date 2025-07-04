from django.urls import path
from .views import (
    UserSignUpView,
    UserLoginView,
    UserProfileView,
)

urlpatterns = [
    path("signup/", UserSignUpView.as_view(), name="user_signup"),
    path("login/", UserLoginView.as_view(), name="user_login"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("update/", UserProfileView.as_view(), name="profile_update"),
]