from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vendor, ReturnRequest, GSTRecord
from .serializers import VendorSerializer, ReturnRequestSerializer, GSTRecordSerializer


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['verification_status']
    search_fields = ['name', 'gstin']
    ordering_fields = ['created_at']


class ReturnRequestViewSet(viewsets.ModelViewSet):
    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['order_id', 'reason']
    ordering_fields = ['requested_at', 'created_at']


class GSTRecordViewSet(viewsets.ModelViewSet):
    queryset = GSTRecord.objects.all()
    serializer_class = GSTRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['record_type']
    search_fields = ['gstin', 'invoice_number']
    ordering_fields = ['invoice_date', 'created_at']