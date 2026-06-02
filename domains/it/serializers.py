# domains/it/serializers.py

from rest_framework import serializers
from .models import Vendor, SoftwareLicense, Incident, ChangeRequest


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_email', 'service_type', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SoftwareLicenseSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = SoftwareLicense
        fields = ['id', 'vendor', 'vendor_name', 'product_name', 'license_key', 'seats', 'expiry_date', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['id', 'title', 'description', 'severity', 'status', 'impact', 'reported_at', 'resolved_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeRequest
        fields = ['id', 'title', 'description', 'change_type', 'risk_level', 'status', 'requested_by', 'scheduled_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
