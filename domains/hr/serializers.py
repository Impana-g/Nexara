# domains/hr/serializers.py

from rest_framework import serializers
from .models import Employee, JobRequisition, OfferLetter, PayrollRecord


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'email', 'department', 'designation', 'employment_type', 'status', 'date_of_joining', 'salary', 'manager_email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class JobRequisitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequisition
        fields = ['id', 'title', 'department', 'budget_min', 'budget_max', 'status', 'requested_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class OfferLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferLetter
        fields = ['id', 'candidate_name', 'candidate_email', 'designation', 'department', 'offered_salary', 'salary_band_min', 'salary_band_max', 'status', 'prepared_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PayrollRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = PayrollRecord
        fields = ['id', 'employee', 'employee_name', 'month', 'basic_salary', 'pf_deduction', 'esi_deduction', 'net_salary', 'is_exception', 'exception_reason', 'approved_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
