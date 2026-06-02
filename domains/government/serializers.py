# domains/government/serializers.py

from rest_framework import serializers
from .models import Tender, Bidder, ProcurementRecord


class TenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = ['id', 'tender_number', 'tender_title', 'status', 'budget', 'publication_date', 'closing_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BidderSerializer(serializers.ModelSerializer):
    tender_number = serializers.CharField(source='tender.tender_number', read_only=True)

    class Meta:
        model = Bidder
        fields = ['id', 'tender', 'tender_number', 'bidder_name', 'bid_amount', 'bid_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProcurementRecordSerializer(serializers.ModelSerializer):
    tender_number = serializers.CharField(source='tender.tender_number', read_only=True)

    class Meta:
        model = ProcurementRecord
        fields = ['id', 'tender', 'tender_number', 'procurement_type', 'vendor_name', 'contract_value', 'contract_date', 'completion_status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
