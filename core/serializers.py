# core/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Tenant, TenantMembership


class TenantSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model  = Tenant
        fields = (
            'id', 'name', 'slug', 'sector',
            'is_active', 'member_count', 'created_at',
        )
        read_only_fields = ('id', 'created_at', 'member_count')

    def get_member_count(self, obj):
        return obj.members.count()


class TenantMembershipSerializer(serializers.ModelSerializer):
    user_email    = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    tenant_name   = serializers.CharField(source='tenant.name', read_only=True)
    tenant_sector = serializers.CharField(source='tenant.sector', read_only=True)

    class Meta:
        model  = TenantMembership
        fields = (
            'id', 'user', 'user_email', 'user_username',
            'tenant', 'tenant_name', 'tenant_sector',
            'role', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


class UserSerializer(serializers.ModelSerializer):
    membership = TenantMembershipSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'membership')
        read_only_fields = ('id',)