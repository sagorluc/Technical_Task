import stripe
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from common import Response
from orders.models import RepairOrder
from payments.celery.task import send_invoice, start_processing
from payments.models import PaymentEvent

logger = logging.getLogger(__name__)


class StripeWebhookAPIView(APIView):
    permission_classes = [AllowAny]
    # authentication_classes = []
    
    def post(self, request, **kwargs):
        payload = request.body
        sig = request.headers.get("Stripe-Signature")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            return Response(success=False, message="Invalid signature", status_code=400)

        event_id = event["id"]

        if PaymentEvent.objects.filter(event_id=event_id).exists(): # idempotency
            return Response(success=False, message="Already processed", status_code=400)

        PaymentEvent.objects.create(event_id=event_id)

        # Handle the event for mobile app checkout
        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            order_id = intent["metadata"]["order_id"]
            amount = intent["amount_received"] / 100

            order = RepairOrder.objects.get(order_id=order_id)

            if order.total_amount != amount:
                return Response(success=False, message="Amount mismatch", status_code=400)

            order.status = "paid"
            order.save()

            send_invoice.delay(order.id)
            start_processing.delay(order.id)
            logger.info("Order %s marked as paid and processing started.", order_id)
            
        # Handle the event for web checkout   
        elif event["type"] == "checkout.session.completed":
            print("Event Data: ", event)
            session = event["data"]["object"]
            order_id = session["metadata"]["order_id"]
            amount = session["amount_total"] / 100

            order = RepairOrder.objects.get(order_id=order_id)

            if order.total_amount != amount:
                return Response(success=False, message="Amount mismatch", status_code=400)

            order.status = "paid"
            order.save()

            send_invoice.delay(order.id)
            start_processing.delay(order.id)
            logger.info("Order %s marked as paid and processing started.", order_id)

        return Response(message="OK", status_code=200)

