from django.urls import path
from . import webhook as payment_views

app_name = "payments"

urlpatterns = [
    path("stripe/webhook/", payment_views.StripeWebhookAPIView.as_view(), name="stripe-webhook"),
]