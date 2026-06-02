# domains/energy/serializers.py

from rest_framework import serializers
from .models import ESGReport, EmissionRecord, CarbonCredit


class ESGReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESGReport
        fields = ['id', 'report_type', 'company_name', 'reporting_year', 'esg_score', 'report_date', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmissionRecordSerializer(serializers.ModelSerializer):
    report_company = serializers.CharField(source='report.company_name', read_only=True)

    class Meta:
        model = EmissionRecord
        fields = ['id', 'report', 'report_company', 'emission_type', 'amount_tonnes', 'record_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CarbonCreditSerializer(serializers.ModelSerializer):
    report_company = serializers.CharField(source='report.company_name', read_only=True)

    class Meta:
        model = CarbonCredit
        fields = ['id', 'report', 'report_company', 'credit_amount', 'credit_type', 'issue_date', 'expiry_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
