# domains/manufacturing/serializers.py

from rest_framework import serializers
from .models import Batch, QualityInspection, DefectRecord


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'batch_number', 'product_name', 'quantity', 'status', 'start_date', 'completion_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class QualityInspectionSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)

    class Meta:
        model = QualityInspection
        fields = ['id', 'batch', 'batch_number', 'inspection_date', 'pass_fail', 'defect_count', 'inspector_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DefectRecordSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)

    class Meta:
        model = DefectRecord
        fields = ['id', 'batch', 'batch_number', 'defect_type', 'severity', 'quantity_defective', 'root_cause', 'resolution_status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
