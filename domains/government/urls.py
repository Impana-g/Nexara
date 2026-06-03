from rest_framework.routers import DefaultRouter
from .views import TenderViewSet, BidderViewSet, ProcurementRecordViewSet

router = DefaultRouter()
router.register(r'tenders',              TenderViewSet,            basename='tender')
router.register(r'bidders',              BidderViewSet,            basename='bidder')
router.register(r'procurement-records',  ProcurementRecordViewSet, basename='procurement-record')

urlpatterns = router.urls