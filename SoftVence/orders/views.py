import stripe
from orders.models import RepairOrder
from orders.serializers import RepairOrderRetriveListSerializer
from payments.models import PaymentEvent, Payment
from rest_framework import status
from common import Response, ValidationError
from services.models import ServiceVariant
from vendors.models import Vendor
from rest_framework.views import APIView
from drf_spectacular.utils import inline_serializer, extend_schema
from rest_framework import serializers as drf_serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def _get_valid_vendor(self, vendor_id):
        if not vendor_id:
            raise ValidationError("Vendor ID is required")
        vendor = Vendor.objects.get(id=vendor_id)
        if not vendor:
            raise ValidationError("Vendor does not exist")
        
        return vendor
    
    def _get_valid_service_variant(self, vendor, variant_id):
        if not variant_id:
            raise ValidationError("Service Variant ID is required")
        variant = ServiceVariant.objects.get(id=variant_id, service__vendor=vendor)
        if not variant:
            raise ValidationError("Service Variant does not exist for the given vendor")
        return variant

    @extend_schema(
        summary="Create Repair Order",
        description="Customer creates a repair order for a service variant provided by a vendor.",
        request=inline_serializer(
            name="CreateOrderSerializer",
            fields={
                "vendor_id": drf_serializers.IntegerField(
                    required=True,
                ),
                "variant_id": drf_serializers.IntegerField(
                    required=True,
                ),
            },
        ),
        responses={
            201: RepairOrderRetriveListSerializer,
            400: ValidationError,
        },
    )
    def post(self, request, **kwargs):
        try:
            MIN_STRIPE_BDT = 60
            
            print("Data: ", request.data)
            print("Data kwargs: ", kwargs.items())
            
            vendor_id =  request.data.get("vendor_id")
            variant_id = request.data.get("variant_id")
            vendor = self._get_valid_vendor(vendor_id)
            variant = self._get_valid_service_variant(vendor, variant_id)

            order = RepairOrder.objects.create(
                customer=request.user,
                vendor=vendor,
                variant=variant,
                total_amount=variant.price,
                status="pending"
            )
            if order.total_amount < MIN_STRIPE_BDT:
                raise ValidationError(
                    f"Minimum payment amount is ৳{MIN_STRIPE_BDT} for online payment."
                )
                
            # ======= Payment Intent for mobile app =======
            # intent = stripe.PaymentIntent.create(
            #     amount=int(order.total_amount * 100), # paisa
            #     currency="bdt",
            #     metadata={
            #         "order_id": str(order.order_id),
            #     },
            # )
            
            # ======= checkout  session for web =======
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": "bdt",
                            "unit_amount": int(order.total_amount * 100),  # paisa
                            "product_data": {
                                "name": f"{variant.name} - {vendor.business_name}",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                metadata={
                    "order_id": str(order.order_id),
                },
                success_url=f"{settings.DOMAIN}/payment/success?order_id=" + str(order.order_id),
                cancel_url=f"{settings.DOMAIN}/payment/cancel?order_id=" + str(order.order_id),
            )

            Payment.objects.create(
                order=order,
                intent_id=session.id,
                amount=order.total_amount,
                status="pending",
            )

            data = {
                "order_id": order.order_id,
                "checkout_url": session.url,
                # "payment_url": intent.next_action["redirect_to_url"]["url"]
            }
            return Response(success=True, data=data, status_code=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                success=False,
                message=e.detail["message"],
                status_code=e.detail["status_code"],
            )