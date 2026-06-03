from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, ReturnRequestViewSet, GSTRecordViewSet

router = DefaultRouter()
router.register(r'vendors',         VendorViewSet,        basename='retail-vendor')
router.register(r'return-requests', ReturnRequestViewSet, basename='return-request')
router.register(r'gst-records',     GSTRecordViewSet,     basename='gst-record')

urlpatterns = router.urls