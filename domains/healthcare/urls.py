from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, PrescriptionViewSet, InsuranceClaimViewSet, ClinicalRecordViewSet

router = DefaultRouter()
router.register(r'patients',         PatientViewSet,         basename='patient')
router.register(r'prescriptions',    PrescriptionViewSet,    basename='prescription')
router.register(r'insurance-claims', InsuranceClaimViewSet,  basename='insurance-claim')
router.register(r'clinical-records', ClinicalRecordViewSet,  basename='clinical-record')

urlpatterns = router.urls