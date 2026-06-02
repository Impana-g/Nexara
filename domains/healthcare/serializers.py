# domains/healthcare/serializers.py

from rest_framework import serializers
from .models import Patient, Prescription, InsuranceClaim, ClinicalRecord


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'mrn', 'full_name', 'dob', 'gender', 'phone', 'email', 'blood_group', 'allergies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)

    class Meta:
        model = Prescription
        fields = ['id', 'patient', 'patient_name', 'medication', 'dosage', 'frequency', 'duration_days', 'prescribed_date', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InsuranceClaimSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)

    class Meta:
        model = InsuranceClaim
        fields = ['id', 'patient', 'patient_name', 'claim_number', 'claim_amount', 'claim_date', 'status', 'approved_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClinicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)

    class Meta:
        model = ClinicalRecord
        fields = ['id', 'patient', 'patient_name', 'visit_date', 'diagnosis', 'notes', 'vitals_bp', 'vitals_temp', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
