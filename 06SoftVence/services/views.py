from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from common.validation_err import ValidationError
from services.models import Service, ServiceVariant
from .serializers import ServiceVariantSerializer, ServiceCreateUpdateSerializer, ServiceRetriveListSerializer, ServiceVariantCreateUpdateSerializer, ServiceVariantResponseSerializer, ServiceApproveSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import serializers as drf_serializers
from common import Response, IsVendorOrAdmin, IsAdminOrReadOnly
from rest_framework.exceptions import PermissionDenied


@extend_schema_view(
    list=extend_schema(
        summary="List vendor services",
        description="Vendor gets own services, Admin gets all services"
    ),
    retrieve=extend_schema(
        summary="Get vendor service",
        description="Retrieve vendor service details"
    ),
    create=extend_schema(
        summary="Create vendor service",
        description="Vendor creates their service",
        request=ServiceCreateUpdateSerializer,
        responses=ServiceRetriveListSerializer
    ),
    update=extend_schema(
        summary="Update vendor Service",
        request=ServiceCreateUpdateSerializer,
        responses=ServiceRetriveListSerializer
    ),
    partial_update=extend_schema(
        summary="Partially update vendor service",
        request=ServiceCreateUpdateSerializer,
        responses=ServiceRetriveListSerializer
    ),
    destroy=extend_schema(
        summary="Delete vendor service"
    ),
)
class ServiceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsVendorOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Service.objects.all()

        return Service.objects.filter(vendor__user=user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ServiceRetriveListSerializer
        return ServiceCreateUpdateSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "vendor":
            raise PermissionDenied("Only vendors can create services")

        serializer.save()


@extend_schema_view(
    list=extend_schema(
        summary="List vendor service variants",
        description="Vendor gets own service variants, Admin gets all service variants"
    ),
    retrieve=extend_schema(
        summary="Get vendor service variant",
        description="Retrieve vendor service variant details"
    ),
    create=extend_schema(
        summary="Create vendor service variant",
        description="Vendor creates their service variant",
        request=ServiceVariantCreateUpdateSerializer,
        responses=ServiceVariantResponseSerializer
    ),
    update=extend_schema(
        summary="Update vendor service variant",
        request=ServiceVariantSerializer,
        responses=ServiceVariantResponseSerializer
    ),
    partial_update=extend_schema(
        summary="Partially update vendor service variant",
        request=ServiceVariantSerializer,
        responses=ServiceVariantResponseSerializer
    ),
    destroy=extend_schema(
        summary="Delete vendor service variant"
    ),
)
class ServiceVariantViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsVendorOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return ServiceVariant.objects.all()

        return ServiceVariant.objects.filter(service__vendor__user=user)
    
    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ServiceVariantResponseSerializer
        return ServiceVariantCreateUpdateSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        service = serializer.validated_data["service"]
        
        if user.role != "vendor":
            raise PermissionDenied("Only vendors can create service variants")
        
        if service.vendor.user != user:
            raise PermissionDenied("You cannot add variants to another vendor's service")

        serializer.save()
        
class ServiceCustomerListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceRetriveListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "customer":
            return Service.objects.approved()
        raise PermissionDenied("Only customers can view approved services")
    
class ServiceCustomerRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceRetriveListSerializer
    queryset = Service.objects.all()
    
class ServiceAdminApproveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ServiceApproveSerializer,
        responses={200: ServiceRetriveListSerializer},
        summary="Approve or unapprove a service",
        description="Only admin can approve/unapprove a service",
    )
    def patch(self, request, pk):
        user = request.user
        if user.role != "admin":
            raise PermissionDenied("Only admin can approve/unapprove services")

        service = generics.get_object_or_404(Service, pk=pk)
        serializer = ServiceApproveSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=ServiceRetriveListSerializer(service).data, status_code=status.HTTP_200_OK)
