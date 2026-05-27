from django.shortcuts import render

# Create your views here.
# core/views.py

import logging
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from core.models import Tenant, TenantMembership
from core.serializers import TenantSerializer, TenantMembershipSerializer, UserSerializer

logger = logging.getLogger('nexara.core.views')


# ─── Health check ─────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'service': 'nexara-api'})


# ─── Auth ─────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    POST /api/auth/login/
    Body: { "username": "...", "password": "..." }
    Returns: { "token": "...", "user": {...}, "tenant": {...} }
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, _ = Token.objects.get_or_create(user=user)

    tenant_data = None
    try:
        tenant_data = TenantSerializer(user.membership.tenant).data
    except Exception:
        pass  # superuser may have no membership — that's fine

    return Response({
        'token':  token.key,
        'user':   UserSerializer(user).data,
        'tenant': tenant_data,
    })


@api_view(['POST'])
def logout_view(request):
    """
    POST /api/auth/logout/
    Deletes the user's auth token.
    """
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'status': 'logged out'})


@api_view(['GET'])
def me_view(request):
    """
    GET /api/auth/me/
    Returns the current user + their tenant.
    """
    return Response(UserSerializer(request.user).data)


# ─── Tenant ───────────────────────────────────────────────────────────────────

class TenantListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tenants/        — list all tenants (admin only)
    POST /api/tenants/        — create a new tenant
    """
    serializer_class   = TenantSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Admin sees all tenants — bypass TenantAwareManager
        return Tenant.all_objects.all().order_by('-created_at')


class TenantDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/tenants/<slug>/   — retrieve tenant detail
    PATCH /api/tenants/<slug>/   — update tenant
    """
    serializer_class   = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field       = 'slug'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Tenant.all_objects.all()
        # Non-admin can only see their own tenant
        return Tenant.all_objects.filter(
            members__user=self.request.user
        )


# ─── Membership ───────────────────────────────────────────────────────────────

class MembershipListView(generics.ListAPIView):
    """
    GET /api/tenants/<slug>/members/
    Lists all members of the current user's tenant.
    """
    serializer_class   = TenantMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        slug = self.kwargs['slug']
        return TenantMembership.objects.filter(
            tenant__slug=slug
        ).select_related('user', 'tenant')