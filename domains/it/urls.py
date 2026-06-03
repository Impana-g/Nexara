from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, SoftwareLicenseViewSet, IncidentViewSet, ChangeRequestViewSet

router = DefaultRouter()
router.register(r'vendors',           VendorViewSet,          basename='vendor')
router.register(r'software-licenses', SoftwareLicenseViewSet, basename='software-license')
router.register(r'incidents',         IncidentViewSet,        basename='incident')
router.register(r'change-requests',   ChangeRequestViewSet,   basename='change-request')

urlpatterns = router.urls