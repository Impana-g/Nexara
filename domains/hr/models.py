# domains/hr/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


# ─── Employee ─────────────────────────────────────────────────────────────────

class Employee(TenantAwareModel):
    class EmploymentType(models.TextChoices):
        FULL_TIME  = 'full_time',  'Full Time'
        PART_TIME  = 'part_time',  'Part Time'
        CONTRACT   = 'contract',   'Contract'
        INTERN     = 'intern',     'Intern'

    class Status(models.TextChoices):
        ACTIVE     = 'active',     'Active'
        ON_LEAVE   = 'on_leave',   'On Leave'
        TERMINATED = 'terminated', 'Terminated'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name       = models.CharField(max_length=255)
    email           = models.EmailField()
    department      = models.CharField(max_length=100)
    designation     = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices)
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    date_of_joining = models.DateField()
    salary          = models.DecimalField(max_digits=12, decimal_places=2)
    manager_email   = models.EmailField(blank=True)

    class Meta:
        db_table = 'hr_employees'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} — {self.designation}'


# ─── Job Requisition ──────────────────────────────────────────────────────────

class JobRequisition(TenantAwareModel):
    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Draft'
        OPEN      = 'open',      'Open'
        APPROVED  = 'approved',  'Approved'
        CLOSED    = 'closed',    'Closed'

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title       = models.CharField(max_length=255)
    department  = models.CharField(max_length=100)
    budget_min  = models.DecimalField(max_digits=12, decimal_places=2)
    budget_max  = models.DecimalField(max_digits=12, decimal_places=2)
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    requested_by = models.CharField(max_length=255)

    class Meta:
        db_table = 'hr_job_requisitions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.department} [{self.status}]'


# ─── Offer Letter ─────────────────────────────────────────────────────────────

class OfferLetter(TenantAwareModel):
    class Status(models.TextChoices):
        DRAFT    = 'draft',    'Draft'
        PENDING  = 'pending',  'Pending Approval'
        APPROVED = 'approved', 'Approved'
        SENT     = 'sent',     'Sent'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()
    designation    = models.CharField(max_length=100)
    department     = models.CharField(max_length=100)
    offered_salary = models.DecimalField(max_digits=12, decimal_places=2)
    salary_band_min = models.DecimalField(max_digits=12, decimal_places=2)
    salary_band_max = models.DecimalField(max_digits=12, decimal_places=2)
    status         = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    prepared_by    = models.CharField(max_length=255)

    class Meta:
        db_table = 'hr_offer_letters'
        ordering = ['-created_at']

    def __str__(self):
        return f'Offer — {self.candidate_name} ({self.designation})'


# ─── Payroll Record ───────────────────────────────────────────────────────────

class PayrollRecord(TenantAwareModel):
    """Append-only payroll records — never UPDATE."""

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee       = models.ForeignKey(Employee, on_delete=models.PROTECT)
    month          = models.CharField(max_length=7)   # e.g. 2026-05
    basic_salary   = models.DecimalField(max_digits=12, decimal_places=2)
    pf_deduction   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    esi_deduction  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary     = models.DecimalField(max_digits=12, decimal_places=2)
    is_exception   = models.BooleanField(default=False)
    exception_reason = models.TextField(blank=True)
    approved_by    = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table        = 'hr_payroll_records'
        unique_together = ('employee', 'month')
        ordering        = ['-month']

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError('Payroll records are append-only.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.employee.full_name} — {self.month} — {self.net_salary}'