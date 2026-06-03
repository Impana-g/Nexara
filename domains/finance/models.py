# domains/finance/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Portfolio(TenantAwareModel):
    """Client investment portfolio."""

    class RiskProfile(models.TextChoices):
        CONSERVATIVE = 'conservative', 'Conservative'
        MODERATE     = 'moderate',     'Moderate'
        AGGRESSIVE   = 'aggressive',   'Aggressive'

    id                   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio_id         = models.CharField(max_length=100, unique=True)
    client_name          = models.CharField(max_length=255)
    client_risk_tolerance= models.IntegerField(default=50)
    risk_profile         = models.CharField(max_length=20, choices=RiskProfile.choices, default=RiskProfile.MODERATE)
    concentration_limit  = models.FloatField(default=0.20)
    is_active            = models.BooleanField(default=True)
    created_at           = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_portfolios'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.portfolio_id} — {self.client_name}'


class Holding(TenantAwareModel):
    """Single position within a portfolio."""

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio      = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    instrument_uid = models.CharField(max_length=100)
    instrument_name= models.CharField(max_length=255, blank=True)
    asset_class    = models.CharField(max_length=50, blank=True)
    value          = models.FloatField(default=0)
    cost           = models.FloatField(default=0)
    risk_score     = models.FloatField(default=0)
    quantity       = models.FloatField(default=0)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'finance_holdings'
        unique_together = ('portfolio', 'instrument_uid')
        ordering        = ['-value']

    def __str__(self):
        return f'{self.instrument_uid} in {self.portfolio.portfolio_id}'


class PortfolioReview(TenantAwareModel):
    """Generated portfolio review report."""

    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        COMPLETE  = 'complete',  'Complete'
        FAILED    = 'failed',    'Failed'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio       = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='reviews')
    workflow_run_id = models.UUIDField(null=True, blank=True)
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_value     = models.FloatField(default=0)
    pnl             = models.FloatField(default=0)
    pnl_pct         = models.FloatField(default=0)
    narrative       = models.TextField(blank=True)
    risk_summary    = models.TextField(blank=True)
    recommendations = models.JSONField(default=list)
    policy_summary  = models.JSONField(default=dict)
    decision        = models.CharField(max_length=20, blank=True)
    decided_by      = models.CharField(max_length=255, blank=True)
    llm_powered     = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_portfolio_reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f'Review {self.id} — {self.portfolio.portfolio_id} [{self.status}]'