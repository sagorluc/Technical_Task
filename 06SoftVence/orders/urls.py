from django.urls import path
from . import views as view

app_name = "orders"

urlpatterns = [
    path("create/", view.CreateOrderAPIView.as_view(), name="create-order")
]