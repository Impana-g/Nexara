# domains/retail/serializers.py

from rest_framework import serializers
from .models import Vendor, ReturnRequest, GSTRecord


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'vendor_ref', 'business_name', 'registration_number', 'gst_number', 'email', 'phone', 'verification_status', 'onboarded_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReturnRequestSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)

    class Meta:
        model = ReturnRequest
        fields = ['id', 'vendor', 'vendor_name', 'return_request_number', 'product_name', 'quantity_returned', 'reason', 'status', 'request_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class GSTRecordSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)

    class Meta:
        model = GSTRecord
        fields = ['id', 'vendor', 'vendor_name', 'invoice_number', 'gst_amount', 'invoice_date', 'payment_status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
