from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Batch, QualityInspection, DefectRecord
from .serializers import BatchSerializer, QualityInspectionSerializer, DefectRecordSerializer


class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['batch_number', 'product_name']
    ordering_fields = ['production_date', 'created_at']


class QualityInspectionViewSet(viewsets.ModelViewSet):
    queryset = QualityInspection.objects.all()
    serializer_class = QualityInspectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'batch']
    search_fields = ['inspector_name']
    ordering_fields = ['inspection_date', 'created_at']


class DefectRecordViewSet(viewsets.ModelViewSet):
    queryset = DefectRecord.objects.all()
    serializer_class = DefectRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'batch']
    search_fields = ['description']
    ordering_fields = ['detected_at', 'created_at']