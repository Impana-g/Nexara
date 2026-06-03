from rest_framework.routers import DefaultRouter
from .views import PolicyViewSet, ClaimViewSet, FraudFlagViewSet, SettlementViewSet

router = DefaultRouter()
router.register(r'policies',    PolicyViewSet,     basename='policy')
router.register(r'claims',      ClaimViewSet,      basename='claim')
router.register(r'fraud-flags', FraudFlagViewSet,  basename='fraud-flag')
router.register(r'settlements', SettlementViewSet, basename='settlement')

urlpatterns = router.urls