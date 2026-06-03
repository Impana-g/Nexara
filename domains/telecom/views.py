from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Operator, SpectrumLicense, Subscriber
from .serializers import OperatorSerializer, SpectrumLicenseSerializer, SubscriberSerializer


class OperatorViewSet(viewsets.ModelViewSet):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['operator_type']
    search_fields = ['name', 'registration_number']
    ordering_fields = ['created_at']


class SpectrumLicenseViewSet(viewsets.ModelViewSet):
    queryset = SpectrumLicense.objects.all()
    serializer_class = SpectrumLicenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['band_type', 'operator']
    search_fields = ['license_number']
    ordering_fields = ['expiry_date', 'created_at']


class SubscriberViewSet(viewsets.ModelViewSet):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subscriber_type', 'operator']
    search_fields = ['msisdn', 'name']
    ordering_fields = ['activation_date', 'created_at']