from django.urls import path
from . import views as view

app_name = "accounts"

urlpatterns = [
    # Signup
    path("admin/sign-up/", view.AdminSignupAPIView.as_view(), name="admin_sign_up"),
    path("vendor/sign-up/", view.VendorSignupAPIView.as_view(), name="vendor_sign_up"),
    path("customer/sign-up/", view.CustomerSignupAPIView.as_view(), name="customer_sign_up"),
    
    # Login
    path("log-in/", view.LoginAPIView.as_view(), name="log_in"),
]