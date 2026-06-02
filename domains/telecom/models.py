# domains/telecom/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Operator(TenantAwareModel):
    """
    Telecom operator record.
    """
    class OperatorType(models.TextChoices):
        INCUMBENT = 'incumbent', 'Incumbent'
        NEW_ENTRANT = 'new_entrant', 'New Entrant'
        MVNO = 'mvno', 'MVNO'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator_code   = models.CharField(max_length=50)
    name            = models.CharField(max_length=255)
    operator_type   = models.CharField(max_length=20, choices=OperatorType.choices)
    registration_number = models.CharField(max_length=100)
    hq_location     = models.CharField(max_length=255)
    is_active       = models.BooleanField(default=True)

    class Meta:
        db_table = 'operators'
        unique_together = ('tenant', 'operator_code')

    def __str__(self):
        return f'{self.operator_code} — {self.name}'


class SpectrumLicense(TenantAwareModel):
    """
    Spectrum frequency license for a telecom operator.
    """
    class BandType(models.TextChoices):
        _2G  = '2g',  '2G (900/1800 MHz)'
        _3G  = '3g',  '3G (2100 MHz)'
        _4G  = '4g',  '4G LTE (800/900/1800/2100 MHz)'
        _5G  = '5g',  '5G (3.5/28 GHz)'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator        = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='spectrum_licenses')
    license_ref     = models.CharField(max_length=100)
    band_type       = models.CharField(max_length=10, choices=BandType.choices)
    frequency_range = models.CharField(max_length=100)
    bandwidth_mhz   = models.DecimalField(max_digits=10, decimal_places=2)
    issue_date      = models.DateField()
    expiry_date     = models.DateField()
    is_active       = models.BooleanField(default=True)

    class Meta:
        db_table = 'spectrum_licenses'
        unique_together = ('tenant', 'license_ref')

    def __str__(self):
        return f'{self.license_ref} — {self.band_type}'


class Subscriber(TenantAwareModel):
    """
    Telecom subscriber/customer record.
    """
    class SubscriberType(models.TextChoices):
        PREPAID  = 'prepaid',  'Prepaid'
        POSTPAID = 'postpaid', 'Postpaid'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator        = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='subscribers')
    phone_number    = models.CharField(max_length=20)
    subscriber_type = models.CharField(max_length=20, choices=SubscriberType.choices)
    name            = models.CharField(max_length=255)
    email           = models.EmailField(blank=True)
    activation_date = models.DateField()
    is_active       = models.BooleanField(default=True)

    class Meta:
        db_table = 'subscribers'
        unique_together = ('tenant', 'phone_number')

    def __str__(self):
        return f'{self.phone_number} — {self.name}'
