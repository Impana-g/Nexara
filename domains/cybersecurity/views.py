from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import SecurityIncident, ThreatAssessment, RegulatoryNotification
from .serializers import SecurityIncidentSerializer, ThreatAssessmentSerializer, RegulatoryNotificationSerializer


class SecurityIncidentViewSet(viewsets.ModelViewSet):
    queryset = SecurityIncident.objects.all()
    serializer_class = SecurityIncidentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['incident_type', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['detected_at', 'created_at']


class ThreatAssessmentViewSet(viewsets.ModelViewSet):
    queryset = ThreatAssessment.objects.all()
    serializer_class = ThreatAssessmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['threat_level']
    search_fields = ['threat_actor', 'target_system']
    ordering_fields = ['assessed_at', 'created_at']


class RegulatoryNotificationViewSet(viewsets.ModelViewSet):
    queryset = RegulatoryNotification.objects.all()
    serializer_class = RegulatoryNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['reference_number', 'regulator']
    ordering_fields = ['deadline', 'created_at']