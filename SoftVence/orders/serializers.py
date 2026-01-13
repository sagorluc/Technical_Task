from rest_framework import serializers

from services.models import ServiceVariant
from services.serializers import VendorRetrieveSerializer
from .models import RepairOrder
from accounts.models import User


class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role"]
        
class ServiceVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariant
        fields = ["id", "name", "price", "estimated_minutes", "stock"]
        
class RepairOrderRetriveListSerializer(serializers.ModelSerializer):
    customer = CustomerUserSerializer()
    vendor = VendorRetrieveSerializer()
    variant = ServiceVariantSerializer()
    
    class Meta:
        model = RepairOrder
        fields = ["id", "order_id", "status", "total_amount", "customer", "vendor", "variant"]