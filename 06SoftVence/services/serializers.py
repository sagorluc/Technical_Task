from rest_framework import serializers
from .models import Service, ServiceVariant
from vendors.models import Vendor
from accounts.models import User
from common import ValidationError

class VendorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role"]
        
class ServiceResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "is_approved", "is_active"]

class VendorRetrieveSerializer(serializers.ModelSerializer):
    user = VendorUserSerializer()
    
    class Meta:
        model = Vendor
        fields = ["id", "user", "business_name", "address", "is_active"]
        
class ServiceVariantCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariant
        fields = ["id", "service", "name", "price", "estimated_minutes", "stock"]
        
class ServiceVariantResponseSerializer(serializers.ModelSerializer):
    service = ServiceResponseSerializer()
    class Meta:
        model = ServiceVariant
        fields = ["id","name", "price", "estimated_minutes", "stock", "service"]
        
class ServiceVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariant
        fields = ["id", "name", "price", "estimated_minutes", "stock"]
        
class ServiceRetriveListSerializer(serializers.ModelSerializer):
    variants = ServiceVariantSerializer(many=True, read_only=True)
    vendor = VendorRetrieveSerializer()
    
    class Meta:
        model = Service
        fields = ["id", "name", "is_approved", "is_active", "vendor", "variants"]
        
class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Service
        fields = ["id", "name"]
        
    def validate(self, attrs):
        user = self.context.get("user")
        if not user:
            raise ValidationError("User not found.")
        if not attrs["name"]:
            raise ValidationError("Service name are required.")
        if user.role != "vendor":
            raise ValidationError("Not allowed without vendor")
        
        vendor = Vendor.objects.filter(user=user).select_related("user")
        
        if not vendor.exists():
            raise ValidationError("Vendor profile does not exist.")
        
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context.get("user")
        vendor = Vendor.objects.filter(user=user).select_related("user").first()
        service = Service.objects.create(
            vendor=vendor,
            name=validated_data["name"],
        )
        return service
    

class ServiceApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["is_approved"]