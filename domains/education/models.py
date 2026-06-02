# domains/education/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Applicant(TenantAwareModel):
    """
    Student applicant record.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    email           = models.EmailField()
    phone           = models.CharField(max_length=20)
    date_of_birth   = models.DateField()
    application_ref = models.CharField(max_length=100)
    gpa             = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    applied_date    = models.DateField()

    class Meta:
        db_table = 'applicants'
        unique_together = ('tenant', 'application_ref')

    def __str__(self):
        return f'{self.application_ref} — {self.first_name} {self.last_name}'


class Program(TenantAwareModel):
    """
    Educational program or course.
    """
    class Level(models.TextChoices):
        BACHELOR = 'bachelor', 'Bachelor'
        MASTER   = 'master',   'Master'
        PHD      = 'phd',      'PhD'
        DIPLOMA  = 'diploma',  'Diploma'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_code = models.CharField(max_length=50)
    name         = models.CharField(max_length=255)
    level        = models.CharField(max_length=20, choices=Level.choices)
    duration_months = models.IntegerField()
    seats        = models.IntegerField(default=100)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'programs'
        unique_together = ('tenant', 'program_code')

    def __str__(self):
        return f'{self.program_code} — {self.name}'


class Grant(TenantAwareModel):
    """
    Educational grant or scholarship.
    """
    class GrantType(models.TextChoices):
        MERIT    = 'merit',    'Merit-based'
        NEED     = 'need',     'Need-based'
        SPECIFIC = 'specific', 'Specific Group'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grant_ref    = models.CharField(max_length=100)
    grant_type   = models.CharField(max_length=20, choices=GrantType.choices)
    amount       = models.DecimalField(max_digits=15, decimal_places=2)
    description  = models.TextField(blank=True)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'grants'
        unique_together = ('tenant', 'grant_ref')

    def __str__(self):
        return f'{self.grant_ref} — ₹{self.amount}'


class AdmissionRecord(TenantAwareModel):
    """
    Admission decision and enrollment record.
    """
    class DecisionStatus(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        ACCEPTED  = 'accepted',  'Accepted'
        REJECTED  = 'rejected',  'Rejected'
        DEFERRED  = 'deferred',  'Deferred'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant       = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='admission_records')
    program         = models.ForeignKey(Program, on_delete=models.PROTECT)
    decision_status = models.CharField(max_length=20, choices=DecisionStatus.choices, default=DecisionStatus.PENDING)
    decision_date   = models.DateField()
    enrollment_date = models.DateField(null=True, blank=True)
    grant           = models.ForeignKey(Grant, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'admission_records'
        unique_together = ('tenant', 'applicant', 'program')

    def __str__(self):
        return f'{self.applicant.application_ref} — {self.program.program_code}'
