# domains/education/serializers.py

from rest_framework import serializers
from .models import Applicant, Program, Grant, AdmissionRecord


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ['id', 'full_name', 'email', 'gpa', 'test_score', 'application_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['id', 'program_name', 'program_level', 'duration_months', 'tuition_cost', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class GrantSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)

    class Meta:
        model = Grant
        fields = ['id', 'applicant', 'applicant_name', 'grant_amount', 'grant_type', 'awarded_date', 'is_disbursed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdmissionRecordSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    program_name = serializers.CharField(source='program.program_name', read_only=True)

    class Meta:
        model = AdmissionRecord
        fields = ['id', 'applicant', 'applicant_name', 'program', 'program_name', 'admission_date', 'status', 'enrollment_confirmed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
