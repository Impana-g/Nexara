# domains/finance/serializers.py

from rest_framework import serializers
from .models import Portfolio, Holding, PortfolioReview


class HoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Holding
        fields = [
            'id', 'instrument_uid', 'instrument_name', 'asset_class',
            'value', 'cost', 'risk_score', 'quantity', 'updated_at',
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    holdings = HoldingSerializer(many=True, read_only=True)

    class Meta:
        model  = Portfolio
        fields = [
            'id', 'portfolio_id', 'client_name', 'client_risk_tolerance',
            'risk_profile', 'concentration_limit', 'is_active',
            'created_at', 'holdings',
        ]


class PortfolioReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PortfolioReview
        fields = [
            'id', 'portfolio', 'workflow_run_id', 'status',
            'total_value', 'pnl', 'pnl_pct',
            'narrative', 'risk_summary', 'recommendations',
            'policy_summary', 'decision', 'decided_by',
            'llm_powered', 'created_at',
        ]