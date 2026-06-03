# domains/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


# ─── Client ───────────────────────────────────────────────────────────────────

class Client(TenantAwareModel):
    """
    End-investor / client record.
    """
    class RiskProfile(models.TextChoices):
        CONSERVATIVE = 'conservative', 'Conservative'
        MODERATE     = 'moderate',     'Moderate'
        AGGRESSIVE   = 'aggressive',   'Aggressive'

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name      = models.CharField(max_length=255)
    email          = models.EmailField()
    risk_profile   = models.CharField(max_length=20, choices=RiskProfile.choices)
    risk_tolerance = models.IntegerField(default=50)   # 0-100 score
    is_active      = models.BooleanField(default=True)

    class Meta:
        db_table = 'clients'
        unique_together = ('tenant', 'email')

    def __str__(self):
        return f'{self.full_name} ({self.risk_profile})'


# ─── Instrument ───────────────────────────────────────────────────────────────

class Instrument(TenantAwareModel):
    """
    Financial instrument — stock, bond, ETF, etc.
    instrument_uid is the canonical cross-system identifier.
    """
    class AssetClass(models.TextChoices):
        EQUITY       = 'equity',       'Equity'
        FIXED_INCOME = 'fixed_income', 'Fixed Income'
        ETF          = 'etf',          'ETF'
        CASH         = 'cash',         'Cash'
        ALTERNATIVE  = 'alternative',  'Alternative'

    instrument_uid = models.CharField(max_length=50)   # e.g. ISIN or ticker
    name           = models.CharField(max_length=255)
    ticker         = models.CharField(max_length=20, blank=True)
    asset_class    = models.CharField(max_length=20, choices=AssetClass.choices)
    risk_score     = models.IntegerField(default=50)                # 0-100
    currency       = models.CharField(max_length=10, default='USD')
    is_active      = models.BooleanField(default=True)

    class Meta:
        db_table = 'instruments'
        unique_together = ('tenant', 'instrument_uid')

    def __str__(self):
        return f'{self.ticker} — {self.name}'


# ─── Portfolio ────────────────────────────────────────────────────────────────

class Portfolio(TenantAwareModel):
    """
    A client's investment portfolio.
    """
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client      = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='portfolios')
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'portfolios'

    def __str__(self):
        return f'{self.name} ({self.client.full_name})'


# ─── Holding ──────────────────────────────────────────────────────────────────

class Holding(TenantAwareModel):
    """
    A single instrument position within a portfolio.
    """
    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio           = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    instrument          = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    quantity            = models.DecimalField(max_digits=18, decimal_places=6)
    average_cost        = models.DecimalField(max_digits=18, decimal_places=6)
    current_price       = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    ingestion_batch_id  = models.CharField(max_length=64, blank=True)  # non-negotiable day-one pattern

    class Meta:
        db_table        = 'holdings'
        unique_together = ('portfolio', 'instrument')

    @property
    def market_value(self):
        return float(self.quantity) * float(self.current_price)

    @property
    def cost_basis(self):
        return float(self.quantity) * float(self.average_cost)

    @property
    def unrealised_pnl(self):
        return self.market_value - self.cost_basis

    def __str__(self):
        return f'{self.instrument.ticker} x{self.quantity} in {self.portfolio.name}'


# ─── Transaction ──────────────────────────────────────────────────────────────

class Transaction(TenantAwareModel):
    """
    Append-only ledger of all portfolio transactions.
    Never UPDATE — always INSERT a new record.
    """
    class TxType(models.TextChoices):
        BUY      = 'buy',      'Buy'
        SELL     = 'sell',     'Sell'
        DIVIDEND = 'dividend', 'Dividend'
        FEE      = 'fee',      'Fee'

    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio          = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    instrument         = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    tx_type            = models.CharField(max_length=20, choices=TxType.choices)
    quantity           = models.DecimalField(max_digits=18, decimal_places=6)
    price              = models.DecimalField(max_digits=18, decimal_places=6)
    total_value        = models.DecimalField(max_digits=18, decimal_places=6)
    tx_date            = models.DateField()
    ingestion_batch_id = models.CharField(max_length=64, blank=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-tx_date', '-created_at']

    def save(self, *args, **kwargs):
        # Append-only — block updates
        if self.pk:
            raise ValueError('Transactions are append-only and cannot be updated.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.tx_type} {self.quantity} {self.instrument.ticker} @ {self.price}'
    
    from django.db import models

class Gene(models.Model):
    gene_id = models.CharField(max_length=100)
    gene_name = models.CharField(max_length=255)
    chromosome = models.CharField(max_length=50)

class Protein(models.Model):
    protein_id = models.CharField(max_length=100)
    protein_name = models.CharField(max_length=255)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)

class GenomeSequence(models.Model):
    sequence_id = models.CharField(max_length=100)
    organism = models.CharField(max_length=255)
    sequence_data = models.TextField()

class ResearchStudy(models.Model):
    study_name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)