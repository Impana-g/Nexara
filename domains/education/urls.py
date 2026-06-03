from rest_framework.routers import DefaultRouter
from .views import ApplicantViewSet, ProgramViewSet, GrantViewSet, AdmissionRecordViewSet

router = DefaultRouter()
router.register(r'applicants',        ApplicantViewSet,       basename='applicant')
router.register(r'programs',          ProgramViewSet,         basename='program')
router.register(r'grants',            GrantViewSet,           basename='grant')
router.register(r'admission-records', AdmissionRecordViewSet, basename='admission-record')

urlpatterns = router.urls