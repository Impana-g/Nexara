from rest_framework.routers import DefaultRouter
from .views import ShipmentViewSet, CustomsRecordViewSet, CargoItemViewSet

router = DefaultRouter()
router.register(r'shipments',       ShipmentViewSet,      basename='shipment')
router.register(r'customs-records', CustomsRecordViewSet, basename='customs-record')
router.register(r'cargo-items',     CargoItemViewSet,     basename='cargo-item')

urlpatterns = router.urls