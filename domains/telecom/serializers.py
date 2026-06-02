# domains/telecom/serializers.py

from rest_framework import serializers
from .models import Operator, SpectrumLicense, Subscriber


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['id', 'operator_name', 'operator_type', 'license_number', 'coverage_area', 'established_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SpectrumLicenseSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.operator_name', read_only=True)

    class Meta:
        model = SpectrumLicense
        fields = ['id', 'operator', 'operator_name', 'band_type', 'frequency_range', 'bandwidth_mhz', 'license_expiry', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriberSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.operator_name', read_only=True)

    class Meta:
        model = Subscriber
        fields = ['id', 'operator', 'operator_name', 'phone_number', 'subscription_date', 'plan_type', 'monthly_charge', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
