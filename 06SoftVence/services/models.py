from django.db import models
from django.core.exceptions import ValidationError
from vendors.models import Vendor
from common import ValidationError as CommonValidationError
        
class ServiceManager(models.Manager):
    def approved(self):
        return self.filter(is_approved=True, is_active=True)
    def active(self):
        return self.filter(is_active=True)

class Service(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="service_vendor")
    name = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ServiceManager()
    
    def __str__(self):
        return f"{self.name}- vendor: {self.vendor.user.email}"

  
class ServiceVariantManager(models.Manager):
    def available(self):
        return self.filter(stock__gt=0)
    def out_of_stock(self):
        return self.filter(stock__lte=0)

class ServiceVariant(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True, related_name="variants")
    name = models.CharField(max_length=50)   
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_minutes = models.DurationField(default=0)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ServiceVariantManager()

    def __str__(self):
        return f"{self.name}- price: {self.price}"
    
    def clean(self): 
        if self.stock < 0:
            raise ValidationError("Stock cannot be negative")
        return super().clean()
    
    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except ValidationError as e:
            raise CommonValidationError(message=e.message, status_code=400)
        super().save(*args, **kwargs)