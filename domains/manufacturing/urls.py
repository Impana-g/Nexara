from rest_framework.routers import DefaultRouter
from .views import BatchViewSet, QualityInspectionViewSet, DefectRecordViewSet

router = DefaultRouter()
router.register(r'batches',             BatchViewSet,             basename='batch')
router.register(r'quality-inspections', QualityInspectionViewSet, basename='quality-inspection')
router.register(r'defect-records',      DefectRecordViewSet,      basename='defect-record')

urlpatterns = router.urls