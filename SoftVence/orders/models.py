import uuid
from django.db import models
from accounts.models import User
from vendors.models import Vendor
from services.models import ServiceVariant

class RepairOrder(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )

    order_id = models.UUIDField(default=uuid.uuid4, unique=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_customer")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="order_vendor")
    variant = models.ForeignKey(ServiceVariant, on_delete=models.CASCADE, related_name="order_variant")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-id"]
        
    def __str__(self):
        return f"{self.customer.get_full_name} - {self.order_id}"

