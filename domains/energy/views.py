# domains/energy/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ESGReport, EmissionRecord, CarbonCredit
from .serializers import ESGReportSerializer, EmissionRecordSerializer, CarbonCreditSerializer


class ESGReportViewSet(viewsets.ModelViewSet):
    queryset = ESGReport.objects.all()
    serializer_class = ESGReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_verified']
    search_fields = ['company_name']
    ordering_fields = ['esg_score', 'reporting_year', 'created_at']


class EmissionRecordViewSet(viewsets.ModelViewSet):
    queryset = EmissionRecord.objects.all()
    serializer_class = EmissionRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['emission_type', 'report']
    search_fields = ['report__company_name']
    ordering_fields = ['amount_tonnes', 'record_date', 'created_at']


class CarbonCreditViewSet(viewsets.ModelViewSet):
    queryset = CarbonCredit.objects.all()
    serializer_class = CarbonCreditSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['credit_type', 'report']
    search_fields = ['report__company_name']
    ordering_fields = ['credit_amount', 'issue_date', 'expiry_date', 'created_at']
