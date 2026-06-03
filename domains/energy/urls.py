from rest_framework.routers import DefaultRouter
from .views import ESGReportViewSet, EmissionRecordViewSet, CarbonCreditViewSet

router = DefaultRouter()
router.register(r'esg-reports',      ESGReportViewSet,      basename='esg-report')
router.register(r'emission-records', EmissionRecordViewSet, basename='emission-record')
router.register(r'carbon-credits',   CarbonCreditViewSet,   basename='carbon-credit')

urlpatterns = router.urls