from django.contrib import admin
from .models import SecurityIncident, ThreatAssessment, RegulatoryNotification


@admin.register(SecurityIncident)
class SecurityIncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_ref', 'incident_type', 'status', 'severity_level', 'reported_date', 'tenant')
    list_filter = ('incident_type', 'status', 'severity_level', 'reported_date', 'tenant')
    search_fields = ('incident_ref', 'description', 'affected_systems')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ThreatAssessment)
class ThreatAssessmentAdmin(admin.ModelAdmin):
    list_display = ('incident', 'threat_level', 'risk_score', 'assessment_date', 'assessor_name', 'tenant')
    list_filter = ('threat_level', 'assessment_date', 'tenant')
    search_fields = ('incident__incident_ref', 'assessor_name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(RegulatoryNotification)
class RegulatoryNotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_ref', 'incident', 'regulatory_body', 'status', 'deadline_date', 'tenant')
    list_filter = ('status', 'regulatory_body', 'deadline_date', 'tenant')
    search_fields = ('notification_ref', 'incident__incident_ref', 'details')
    readonly_fields = ('id', 'created_at', 'updated_at')
