from rest_framework.routers import DefaultRouter
from .views import OperatorViewSet, SpectrumLicenseViewSet, SubscriberViewSet

router = DefaultRouter()
router.register(r'operators',         OperatorViewSet,        basename='operator')
router.register(r'spectrum-licenses', SpectrumLicenseViewSet, basename='spectrum-license')
router.register(r'subscribers',       SubscriberViewSet,      basename='subscriber')

urlpatterns = router.urls