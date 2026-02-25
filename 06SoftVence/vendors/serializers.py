from rest_framework import serializers
from .models import User, Vendor
from common import ValidationError

class VendorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role"]

class VendorRetrieveSerializer(serializers.ModelSerializer):
    user = VendorUserSerializer()
    
    class Meta:
        model = Vendor
        fields = ["id", "user", "business_name", "address", "is_active"]
        

class VendorCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vendor
        fields = ["business_name", "address"]
        
    def validate(self, attrs):
        user = self.context.get("user")

        if not attrs.get("business_name"):
            raise ValidationError("Business name is required.")

        if not attrs.get("address"):
            raise ValidationError("Address is required.")

        if user.role != "vendor":
            raise ValidationError("Only vendor can create a vendor profile.")

        vendor_qs = Vendor.objects.filter(user=user)
        
        if self.instance:
            vendor_qs = vendor_qs.exclude(id=self.instance.id)

        if vendor_qs.exists():
            raise ValidationError("Vendor profile already exists.")

        return attrs

    def create(self, validated_data):
        user = self.context.get("user")
        vendor = Vendor.objects.create(
            user=user,
            business_name=validated_data["business_name"],
            address=validated_data["address"],
        )
        return vendor