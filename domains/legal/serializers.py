# domains/legal/serializers.py

from rest_framework import serializers
from .models import Contract, Case, Filing, ConflictRecord


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['id', 'contract_number', 'contract_type', 'counterparty', 'value', 'status', 'start_date', 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ['id', 'case_number', 'case_name', 'status', 'court_name', 'judge_name', 'filed_date', 'next_hearing', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FilingSerializer(serializers.ModelSerializer):
    case_name = serializers.CharField(source='case.case_name', read_only=True)

    class Meta:
        model = Filing
        fields = ['id', 'case', 'case_name', 'filing_type', 'filing_date', 'status', 'filed_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConflictRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConflictRecord
        fields = ['id', 'party_name', 'conflict_type', 'severity', 'description', 'resolution_status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
