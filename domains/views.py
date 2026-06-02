from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client, Portfolio, Holding, Instrument, Transaction
from .serializers import ClientSerializer, PortfolioSerializer, HoldingSerializer, InstrumentSerializer, TransactionSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['risk_profile', 'country']
    search_fields = ['full_name', 'email', 'city']
    ordering_fields = ['aum', 'created_at']


class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset_class', 'currency']
    search_fields = ['name', 'isin', 'instrument_uid']
    ordering_fields = ['current_price', 'created_at']


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['portfolio_type', 'status', 'currency']
    search_fields = ['client__full_name']
    ordering_fields = ['total_value', 'created_at']


class HoldingViewSet(viewsets.ModelViewSet):
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['portfolio']
    ordering_fields = ['current_value', 'created_at']


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['portfolio', 'transaction_type']
    search_fields = ['instrument__name']
    ordering_fields = ['transaction_date', 'total_amount', 'created_at']
