import stripe
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product, CartItem
from e_commerce.utils import AuthenticatedUser, Response
from .serializers import (
    CategoryCreateSerializer,
    ProductSerializer,
    ProductCreateSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeCheckoutAPIView(APIView):
    permission_classes = [AuthenticatedUser]

    def post(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response(
                success=False,
                message="Cart is empty",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_amount = sum([item.get_total_price() for item in cart_items])
        total_amount_cents = int(total_amount * 100)

        try:
            intent = stripe.PaymentIntent.create(
                amount=total_amount_cents,
                currency="usd",
                metadata={"user_id": request.user.id},
            )
            stripe_data = {
                "client_secret": intent.client_secret,
                "amount": total_amount,
                "currency": "usd",
            }
            return Response(
                success=True,
                message="successful",
                data=stripe_data,
                status_code=status.HTTP_201_CREATED,
            )
        except stripe.error.StripeError as e:
            return Response(success=False, message=str(e), status_code=500)


class ProductPaginationList(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 1000


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [AuthenticatedUser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "description"]
    pagination_class = ProductPaginationList


class CategoryCreateAPIView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [AuthenticatedUser]


class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [AuthenticatedUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)
