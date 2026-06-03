from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, JobRequisitionViewSet, OfferLetterViewSet, PayrollRecordViewSet

router = DefaultRouter()
router.register(r'employees',         EmployeeViewSet,        basename='employee')
router.register(r'job-requisitions',  JobRequisitionViewSet,  basename='job-requisition')
router.register(r'offer-letters',     OfferLetterViewSet,     basename='offer-letter')
router.register(r'payroll-records',   PayrollRecordViewSet,   basename='payroll-record')

urlpatterns = router.urls