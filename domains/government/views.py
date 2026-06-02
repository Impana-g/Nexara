# domains/government/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tender, Bidder, ProcurementRecord
from .serializers import TenderSerializer, BidderSerializer, ProcurementRecordSerializer


class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['tender_number', 'tender_title']
    ordering_fields = ['budget', 'closing_date', 'created_at']


class BidderViewSet(viewsets.ModelViewSet):
    queryset = Bidder.objects.all()
    serializer_class = BidderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'tender']
    search_fields = ['bidder_name']
    ordering_fields = ['bid_amount', 'bid_date', 'created_at']


class ProcurementRecordViewSet(viewsets.ModelViewSet):
    queryset = ProcurementRecord.objects.all()
    serializer_class = ProcurementRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['procurement_type', 'completion_status']
    search_fields = ['vendor_name', 'tender__tender_number']
    ordering_fields = ['contract_value', 'contract_date', 'created_at']
