from django.db import models
from orders.models import RepairOrder
from decimal import Decimal
    
class Payment(models.Model):
    CHOICESS = (
            ("pending", "Pending"),
            ("succeeded", "Succeeded"),
            ("failed", "Failed"),
        )
    order = models.OneToOneField(RepairOrder, on_delete=models.CASCADE, related_name="payment_order")
    intent_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=255, choices=CHOICESS, default="pending")
    raw_response = models.JSONField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-id"]
    
    def __str__(self):
        return f"{self.order.order_id} - {self.status}"
    
class PaymentEvent(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payment_events"
    )
    event_id = models.CharField(max_length=255, unique=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Event ID: {self.event_id}"

