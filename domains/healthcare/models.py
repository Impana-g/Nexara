# domains/healthcare/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Patient(TenantAwareModel):
    """
    Patient record.
    """
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mrn            = models.CharField(max_length=100)  # Medical Record Number
    first_name     = models.CharField(max_length=100)
    last_name      = models.CharField(max_length=100)
    date_of_birth  = models.DateField()
    email          = models.EmailField()
    phone          = models.CharField(max_length=20, blank=True)
    is_active      = models.BooleanField(default=True)

    class Meta:
        db_table = 'patients'
        unique_together = ('tenant', 'mrn')

    def __str__(self):
        return f'{self.mrn} — {self.first_name} {self.last_name}'


class Prescription(TenantAwareModel):
    """
    Prescription record for a patient.
    """
    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient            = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name    = models.CharField(max_length=255)
    dosage             = models.CharField(max_length=100)
    frequency          = models.CharField(max_length=100)
    prescribed_date    = models.DateField()
    expiry_date        = models.DateField(null=True, blank=True)
    quantity           = models.IntegerField()
    notes              = models.TextField(blank=True)

    class Meta:
        db_table = 'prescriptions'
        ordering = ['-prescribed_date']

    def __str__(self):
        return f'{self.medication_name} for {self.patient.mrn}'


class InsuranceClaim(TenantAwareModel):
    """
    Health insurance claim.
    """
    class Status(models.TextChoices):
        PENDING    = 'pending',    'Pending'
        APPROVED   = 'approved',   'Approved'
        REJECTED   = 'rejected',   'Rejected'
        PAID       = 'paid',       'Paid'

    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient            = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_claims')
    claim_ref          = models.CharField(max_length=100)
    claim_amount       = models.DecimalField(max_digits=18, decimal_places=2)
    status             = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    claim_date         = models.DateField()
    resolution_date    = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'insurance_claims'
        unique_together = ('tenant', 'claim_ref')

    def __str__(self):
        return f'{self.claim_ref} — ₹{self.claim_amount}'


class ClinicalRecord(TenantAwareModel):
    """
    Clinical notes and observations.
    """
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient        = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='clinical_records')
    visit_date     = models.DateField()
    diagnosis      = models.TextField()
    treatment_plan = models.TextField()
    notes          = models.TextField(blank=True)
    physician_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'clinical_records'
        ordering = ['-visit_date']

    def __str__(self):
        return f'{self.patient.mrn} — {self.visit_date}'
