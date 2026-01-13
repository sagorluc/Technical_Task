from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from common.validation_err import ValidationError
from vendors.models import Vendor
from .serializers import VendorCreateUpdateSerializer, VendorRetrieveSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from common import Response, IsVendorOrAdmin
from django.db import transaction
from rest_framework.exceptions import PermissionDenied


@extend_schema_view(
    list=extend_schema(
        summary="List vendor profiles",
        description="Vendor gets own profile, Admin gets all vendors"
    ),
    retrieve=extend_schema(
        summary="Get vendor profile",
        description="Retrieve vendor business profile"
    ),
    create=extend_schema(
        summary="Create vendor business profile",
        description="Vendor creates their business profile",
        request=VendorCreateUpdateSerializer,
        responses=VendorRetrieveSerializer
    ),
    update=extend_schema(
        summary="Update vendor profile",
        request=VendorCreateUpdateSerializer,
        responses=VendorRetrieveSerializer
    ),
    partial_update=extend_schema(
        summary="Partially update vendor profile",
        request=VendorCreateUpdateSerializer,
        responses=VendorRetrieveSerializer
    ),
    destroy=extend_schema(
        summary="Delete vendor profile"
    ),
)
class VendorBusinessProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsVendorOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Vendor.objects.all()

        return Vendor.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return VendorRetrieveSerializer
        return VendorCreateUpdateSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "vendor":
            raise PermissionDenied("Only vendors can create profiles")

        with transaction.atomic():
            if Vendor.objects.select_for_update().filter(user=user).exists():
                raise PermissionDenied("Vendor profile already exists")

        serializer.save(user=user)
