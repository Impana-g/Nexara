# domains/insurance/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Policy, Claim, FraudFlag, Settlement
from .serializers import PolicySerializer, ClaimSerializer, FraudFlagSerializer, SettlementSerializer


class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['policy_type', 'status']
    search_fields = ['policy_number', 'customer_name']
    ordering_fields = ['premium_amount', 'created_at']


class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'policy']
    search_fields = ['claim_number']
    ordering_fields = ['claim_date', 'claim_amount', 'created_at']


class FraudFlagViewSet(viewsets.ModelViewSet):
    queryset = FraudFlag.objects.all()
    serializer_class = FraudFlagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'is_resolved']
    search_fields = ['claim__claim_number', 'reason']
    ordering_fields = ['flagged_date', 'severity', 'created_at']


class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method']
    search_fields = ['claim__claim_number']
    ordering_fields = ['settlement_date', 'settlement_amount', 'created_at']
