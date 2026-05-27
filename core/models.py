

# Create your models here.
# core/models.py

import uuid
from django.db import models
from django.contrib.auth.models import User


# ─── Sector Choices ───────────────────────────────────────────────────────────

class SectorChoices(models.TextChoices):
    FINANCE      = 'finance',      'Finance & Wealth Management'
    IT           = 'it',           'IT / Technology'
    HR           = 'hr',           'HR / People Operations'
    LEGAL        = 'legal',        'Legal'
    HEALTHCARE   = 'healthcare',   'Healthcare'
    INSURANCE    = 'insurance',    'Insurance'
    EDUCATION    = 'education',    'Education'
    GOVERNMENT   = 'government',   'Government / Public Sector'
    ENERGY       = 'energy',       'Energy'
    TELECOM      = 'telecom',      'Telecom'
    MANUFACTURING = 'manufacturing','Manufacturing'
    LOGISTICS    = 'logistics',    'Logistics / Supply Chain'
    RETAIL       = 'retail',       'Retail / E-commerce'
    CYBERSECURITY = 'cybersecurity','Cybersecurity'


# ─── Tenant ───────────────────────────────────────────────────────────────────

class Tenant(models.Model):
    """
    One row per organisation that signs up.
    sector determines which workflows, nodes, and policy rules are available.
    """
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name       = models.CharField(max_length=255)
    sector     = models.CharField(max_length=50, choices=SectorChoices.choices)
    slug       = models.SlugField(unique=True)          # used in API paths
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenants'

    def __str__(self):
        return f'{self.name} ({self.sector})'


# ─── Tenant Membership ────────────────────────────────────────────────────────

class TenantMembership(models.Model):
    """
    Links a Django User to a Tenant with a role.
    A user can belong to only one tenant at a time.
    """
    class Role(models.TextChoices):
        ADMIN    = 'admin',    'Admin'
        REVIEWER = 'reviewer', 'Reviewer'       # can action HITL decisions
        ANALYST  = 'analyst',  'Analyst'         # read + trigger workflows
        VIEWER   = 'viewer',   'Viewer'           # read-only

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    tenant     = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='members')
    role       = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tenant_memberships'

    def __str__(self):
        return f'{self.user.email} → {self.tenant.name} [{self.role}]'


# ─── Tenant-Aware Manager ─────────────────────────────────────────────────────

class TenantAwareManager(models.Manager):
    """
    Auto-filters every queryset to the current request's tenant.
    Views never need to filter manually — it's enforced at ORM level.
    """
    def get_queryset(self):
        from core.middleware import get_current_tenant
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is not None:
            return qs.filter(tenant=tenant)
        return qs


# ─── Tenant-Aware Abstract Base ───────────────────────────────────────────────

class TenantAwareModel(models.Model):
    """
    Abstract base class for every domain model in Nexara.
    Inherit this instead of models.Model.

    Usage:
        class Portfolio(TenantAwareModel):
            name = models.CharField(max_length=255)
            # tenant field and TenantAwareManager come for free
    """
    tenant     = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects    = TenantAwareManager()       # filtered by tenant
    all_objects = models.Manager()          # unfiltered — use carefully (admin, internal APIs only)

    class Meta:
        abstract = True
