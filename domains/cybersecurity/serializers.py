# domains/cybersecurity/serializers.py

from rest_framework import serializers
from .models import SecurityIncident, ThreatAssessment, RegulatoryNotification


class SecurityIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityIncident
        fields = ['id', 'incident_title', 'incident_type', 'severity', 'reported_date', 'status', 'affected_systems', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ThreatAssessmentSerializer(serializers.ModelSerializer):
    incident_title = serializers.CharField(source='incident.incident_title', read_only=True)

    class Meta:
        model = ThreatAssessment
        fields = ['id', 'incident', 'incident_title', 'threat_level', 'assessment_date', 'recommendations', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegulatoryNotificationSerializer(serializers.ModelSerializer):
    incident_title = serializers.CharField(source='incident.incident_title', read_only=True)

    class Meta:
        model = RegulatoryNotification
        fields = ['id', 'incident', 'incident_title', 'regulation', 'notification_date', 'compliance_deadline', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
