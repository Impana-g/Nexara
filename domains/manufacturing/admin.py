from django.contrib import admin
from .models import Batch, QualityInspection, DefectRecord


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_ref', 'product_name', 'quantity', 'status', 'start_date', 'tenant')
    list_filter = ('status', 'start_date', 'completion_date', 'tenant')
    search_fields = ('batch_ref', 'product_name', 'line_number')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display = ('batch', 'inspection_date', 'inspector_name', 'status', 'defect_rate_percent', 'tenant')
    list_filter = ('status', 'inspection_date', 'tenant')
    search_fields = ('batch__batch_ref', 'inspector_name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(DefectRecord)
class DefectRecordAdmin(admin.ModelAdmin):
    list_display = ('defect_code', 'inspection', 'severity', 'location', 'tenant')
    list_filter = ('severity', 'tenant', 'created_at')
    search_fields = ('defect_code', 'description', 'location')
    readonly_fields = ('id', 'created_at', 'updated_at')
