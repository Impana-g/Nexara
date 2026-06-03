from rest_framework.routers import DefaultRouter
from .views import ContractViewSet, CaseViewSet, FilingViewSet, ConflictRecordViewSet

router = DefaultRouter()
router.register(r'contracts',        ContractViewSet,        basename='contract')
router.register(r'cases',            CaseViewSet,            basename='case')
router.register(r'filings',          FilingViewSet,          basename='filing')
router.register(r'conflict-records', ConflictRecordViewSet,  basename='conflict-record')

urlpatterns = router.urls