# domains/finance/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Portfolio, Holding, PortfolioReview
from .serializers import PortfolioSerializer, HoldingSerializer, PortfolioReviewSerializer


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'risk_profile']
    search_fields = ['portfolio_id', 'client_name']
    ordering_fields = ['created_at', 'client_name']


class HoldingViewSet(viewsets.ModelViewSet):
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['portfolio', 'asset_class']
    search_fields = ['instrument_uid', 'instrument_name']
    ordering_fields = ['value', 'risk_score', 'updated_at']


class PortfolioReviewViewSet(viewsets.ModelViewSet):
    queryset = PortfolioReview.objects.all()
    serializer_class = PortfolioReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'decision', 'llm_powered']
    search_fields = ['portfolio__portfolio_id', 'portfolio__client_name']
    ordering_fields = ['created_at', 'total_value', 'pnl']