from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as view

app_name = "vendor"

router = DefaultRouter()
router.register("", view.VendorBusinessProfileViewSet, basename="vendors")
urlpatterns = router.urls

# urlpatterns = [
#     path("profile/create/", view.VendorBusinessProfileViewSet.as_view(), name="vendor_profile_create")
# ]