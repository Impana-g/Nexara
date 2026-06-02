# domains/insurance/serializers.py

from rest_framework import serializers
from .models import Policy, Claim, FraudFlag, Settlement


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['id', 'policy_number', 'policy_type', 'customer_name', 'premium_amount', 'coverage_amount', 'start_date', 'end_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClaimSerializer(serializers.ModelSerializer):
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)

    class Meta:
        model = Claim
        fields = ['id', 'policy', 'policy_number', 'claim_number', 'claim_amount', 'claim_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FraudFlagSerializer(serializers.ModelSerializer):
    claim_number = serializers.CharField(source='claim.claim_number', read_only=True)

    class Meta:
        model = FraudFlag
        fields = ['id', 'claim', 'claim_number', 'reason', 'severity', 'flagged_date', 'is_resolved', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SettlementSerializer(serializers.ModelSerializer):
    claim_number = serializers.CharField(source='claim.claim_number', read_only=True)

    class Meta:
        model = Settlement
        fields = ['id', 'claim', 'claim_number', 'settlement_amount', 'settlement_date', 'payment_method', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
