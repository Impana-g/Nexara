from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shipment, CustomsRecord, CargoItem
from .serializers import ShipmentSerializer, CustomsRecordSerializer, CargoItemSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['tracking_number', 'origin', 'destination']
    ordering_fields = ['expected_delivery', 'created_at']


class CustomsRecordViewSet(viewsets.ModelViewSet):
    queryset = CustomsRecord.objects.all()
    serializer_class = CustomsRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clearance_status']
    search_fields = ['declaration_number']
    ordering_fields = ['declaration_date', 'created_at']


class CargoItemViewSet(viewsets.ModelViewSet):
    queryset = CargoItem.objects.all()
    serializer_class = CargoItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shipment']
    search_fields = ['description', 'hs_code']
    ordering_fields = ['weight_kg', 'created_at']