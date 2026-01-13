from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views as view

app_name = "services"

router = DefaultRouter()
router.register("services", view.ServiceViewSet, basename="services")
router.register("service-variant", view.ServiceVariantViewSet, basename="service_variants")
urlpatterns = router.urls

urlpatterns += [
    path("customer/list/", view.ServiceCustomerListView.as_view(), name="service-list"),
    path("customer/<int:pk>/", view.ServiceCustomerRetrieveView.as_view(), name="service-detail"),
    path("admin/<int:pk>/approve/", view.ServiceAdminApproveAPIView.as_view(), name="service-approve"),
]