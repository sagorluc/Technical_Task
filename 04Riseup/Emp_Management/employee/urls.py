# leaves/urls.py
from rest_framework.routers import DefaultRouter
from .views import LeaveRequestViewSet

router = DefaultRouter()
router.register(r"leaves", LeaveRequestViewSet, basename="leave-request")

urlpatterns = router.urls

