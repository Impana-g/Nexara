# domains/serializers.py

from rest_framework import serializers
from .models import Client, Portfolio, Holding, Instrument, Transaction


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'email', 'full_name', 'phone', 'city', 'country', 'aum', 'risk_profile', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ['id', 'instrument_uid', 'isin', 'name', 'asset_class', 'currency', 'current_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class HoldingSerializer(serializers.ModelSerializer):
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)

    class Meta:
        model = Holding
        fields = ['id', 'portfolio', 'instrument', 'instrument_name', 'units', 'average_cost', 'current_value', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'portfolio', 'instrument', 'instrument_name', 'transaction_type', 'quantity', 'price_per_unit', 'total_amount', 'transaction_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PortfolioSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    holdings = HoldingSerializer(many=True, read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'client', 'client_name', 'portfolio_type', 'total_value', 'currency', 'status', 'holdings', 'transactions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
