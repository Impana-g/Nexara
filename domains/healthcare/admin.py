from django.contrib import admin
from .models import Patient, Prescription, InsuranceClaim, ClinicalRecord


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('mrn', 'first_name', 'last_name', 'email', 'tenant')
    list_filter = ('is_active', 'tenant', 'created_at')
    search_fields = ('mrn', 'first_name', 'last_name', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medication_name', 'patient', 'dosage', 'prescribed_date', 'tenant')
    list_filter = ('prescribed_date', 'tenant', 'created_at')
    search_fields = ('medication_name', 'patient__mrn')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_ref', 'patient', 'claim_amount', 'status', 'tenant')
    list_filter = ('status', 'claim_date', 'tenant')
    search_fields = ('claim_ref', 'patient__mrn')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ClinicalRecord)
class ClinicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'visit_date', 'physician_name', 'tenant')
    list_filter = ('visit_date', 'tenant', 'created_at')
    search_fields = ('patient__mrn', 'physician_name', 'diagnosis')
    readonly_fields = ('id', 'created_at', 'updated_at')
