# domains/it/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vendor, SoftwareLicense, Incident, ChangeRequest
from .serializers import VendorSerializer, SoftwareLicenseSerializer, IncidentSerializer, ChangeRequestSerializer


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'service_type']
    search_fields = ['name', 'contact_email']


class SoftwareLicenseViewSet(viewsets.ModelViewSet):
    queryset = SoftwareLicense.objects.all()
    serializer_class = SoftwareLicenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vendor', 'is_active']
    search_fields = ['product_name']
    ordering_fields = ['expiry_date', 'created_at']


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['reported_at', 'severity', 'created_at']


class ChangeRequestViewSet(viewsets.ModelViewSet):
    queryset = ChangeRequest.objects.all()
    serializer_class = ChangeRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['change_type', 'risk_level', 'status']
    search_fields = ['title', 'requested_by']
    ordering_fields = ['scheduled_date', 'created_at']
