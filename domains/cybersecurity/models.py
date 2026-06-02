# domains/cybersecurity/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class SecurityIncident(TenantAwareModel):
    """
    Security incident or breach record.
    """
    class IncidentType(models.TextChoices):
        MALWARE         = 'malware',         'Malware'
        PHISHING        = 'phishing',        'Phishing'
        DATA_BREACH     = 'data_breach',     'Data Breach'
        UNAUTHORIZED_ACCESS = 'unauth_access', 'Unauthorized Access'
        DDOS            = 'ddos',            'DDoS Attack'
        OTHER           = 'other',           'Other'

    class IncidentStatus(models.TextChoices):
        REPORTED       = 'reported',       'Reported'
        INVESTIGATING  = 'investigating',  'Investigating'
        CONTAINED      = 'contained',      'Contained'
        RESOLVED       = 'resolved',       'Resolved'
        ESCALATED      = 'escalated',      'Escalated'

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident_ref      = models.CharField(max_length=100)
    incident_type     = models.CharField(max_length=30, choices=IncidentType.choices)
    status            = models.CharField(max_length=20, choices=IncidentStatus.choices, default=IncidentStatus.REPORTED)
    description       = models.TextField()
    severity_level    = models.IntegerField(default=50)  # 0-100
    affected_systems  = models.CharField(max_length=500)
    reported_date     = models.DateTimeField()
    detected_date     = models.DateTimeField()
    resolved_date     = models.DateTimeField(null=True, blank=True)
    affected_records  = models.IntegerField(default=0)

    class Meta:
        db_table = 'security_incidents'
        unique_together = ('tenant', 'incident_ref')

    def __str__(self):
        return f'{self.incident_ref} — {self.incident_type}'


class ThreatAssessment(TenantAwareModel):
    """
    Threat assessment and risk analysis record.
    """
    class ThreatLevel(models.TextChoices):
        LOW      = 'low',      'Low'
        MEDIUM   = 'medium',   'Medium'
        HIGH     = 'high',     'High'
        CRITICAL = 'critical', 'Critical'

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident            = models.OneToOneField(SecurityIncident, on_delete=models.CASCADE, related_name='threat_assessment')
    threat_level        = models.CharField(max_length=20, choices=ThreatLevel.choices)
    likelihood_score    = models.IntegerField(default=50)  # 0-100
    impact_score        = models.IntegerField(default=50)  # 0-100
    risk_score          = models.IntegerField(default=50)  # 0-100 (computed)
    mitigation_strategy = models.TextField()
    assessment_date     = models.DateField()
    assessor_name       = models.CharField(max_length=255)

    class Meta:
        db_table = 'threat_assessments'

    def __str__(self):
        return f'{self.incident.incident_ref} — {self.threat_level}'


class RegulatoryNotification(TenantAwareModel):
    """
    Regulatory notification requirement (e.g., GDPR, CCPA breach notification).
    """
    class NotificationStatus(models.TextChoices):
        PENDING      = 'pending',      'Pending'
        SUBMITTED    = 'submitted',    'Submitted'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
        CLOSED       = 'closed',       'Closed'

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident            = models.ForeignKey(SecurityIncident, on_delete=models.CASCADE, related_name='regulatory_notifications')
    notification_ref    = models.CharField(max_length=100)
    regulatory_body     = models.CharField(max_length=255)
    notification_type   = models.CharField(max_length=100)  # e.g. "GDPR Breach", "CCPA Data Sale"
    status              = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    deadline_date       = models.DateField()
    submitted_date      = models.DateField(null=True, blank=True)
    acknowledgement_ref = models.CharField(max_length=100, blank=True)
    details             = models.TextField()

    class Meta:
        db_table = 'regulatory_notifications'
        unique_together = ('tenant', 'notification_ref')

    def __str__(self):
        return f'{self.notification_ref} — {self.regulatory_body}'
