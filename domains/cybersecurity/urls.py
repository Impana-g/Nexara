from rest_framework.routers import DefaultRouter
from .views import SecurityIncidentViewSet, ThreatAssessmentViewSet, RegulatoryNotificationViewSet

router = DefaultRouter()
router.register(r'security-incidents',       SecurityIncidentViewSet,       basename='security-incident')
router.register(r'threat-assessments',       ThreatAssessmentViewSet,       basename='threat-assessment')
router.register(r'regulatory-notifications', RegulatoryNotificationViewSet, basename='regulatory-notification')

urlpatterns = router.urls