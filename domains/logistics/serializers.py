# domains/logistics/serializers.py

from rest_framework import serializers
from .models import Shipment, CustomsRecord, CargoItem


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['id', 'shipment_number', 'origin', 'destination', 'status', 'shipment_date', 'expected_delivery', 'actual_delivery', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomsRecordSerializer(serializers.ModelSerializer):
    shipment_number = serializers.CharField(source='shipment.shipment_number', read_only=True)

    class Meta:
        model = CustomsRecord
        fields = ['id', 'shipment', 'shipment_number', 'hs_code', 'customs_cleared', 'clearance_date', 'duty_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CargoItemSerializer(serializers.ModelSerializer):
    shipment_number = serializers.CharField(source='shipment.shipment_number', read_only=True)

    class Meta:
        model = CargoItem
        fields = ['id', 'shipment', 'shipment_number', 'item_description', 'quantity', 'weight_kg', 'hs_code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
