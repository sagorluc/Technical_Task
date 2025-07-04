from django.urls import path
from . import views

urlpatterns = [
    path(
        "category/create/",
        views.CategoryCreateAPIView.as_view(),
        name="product_category_create",
    ),
    path("list/", views.ProductListAPIView.as_view(), name="product_list"),
    path("create/", views.ProductCreateAPIView.as_view(), name="product_create"),
    path("checkout/", views.StripeCheckoutAPIView.as_view(), name="stripe-checkout"),
]
