# domains/legal/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Contract, Case, Filing, ConflictRecord
from .serializers import ContractSerializer, CaseSerializer, FilingSerializer, ConflictRecordSerializer


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['contract_type', 'status']
    search_fields = ['contract_number', 'counterparty']
    ordering_fields = ['value', 'end_date', 'created_at']


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'court_name']
    search_fields = ['case_name', 'case_number']
    ordering_fields = ['filed_date', 'next_hearing', 'created_at']


class FilingViewSet(viewsets.ModelViewSet):
    queryset = Filing.objects.all()
    serializer_class = FilingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['filing_type', 'status']
    search_fields = ['case__case_name', 'filed_by']
    ordering_fields = ['filing_date', 'created_at']


class ConflictRecordViewSet(viewsets.ModelViewSet):
    queryset = ConflictRecord.objects.all()
    serializer_class = ConflictRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conflict_type', 'severity', 'resolution_status']
    search_fields = ['party_name', 'description']
    ordering_fields = ['severity', 'created_at']
