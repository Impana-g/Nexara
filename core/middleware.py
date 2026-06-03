# core/middleware.py

import threading
import logging

logger = logging.getLogger('nexara.core.middleware')

_thread_locals = threading.local()


def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    _thread_locals.tenant = tenant


def clear_current_tenant():
    _thread_locals.tenant = None


class TenantMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = self._resolve_tenant(request)

        if tenant is not None:
            set_current_tenant(tenant)
            request.tenant = tenant
            logger.debug(f'Tenant resolved: {tenant.name} ({tenant.sector})')
        else:
            clear_current_tenant()
            request.tenant = None

        response = self.get_response(request)
        clear_current_tenant()
        return response

    def _resolve_tenant(self, request):
        path = request.path_info
        if path.startswith('/admin/') or path == '/health/':
            return None

        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            return self._get_tenant_by_id(tenant_id)

        slug = request.headers.get('X-Tenant-Slug')
        if slug:
            return self._get_tenant_by_slug(slug)

        if hasattr(request, 'user') and request.user.is_authenticated:
            return self._get_tenant_from_user(request.user)

        return None

    def _get_tenant_by_id(self, tenant_id):
        from core.models import Tenant
        try:
            return Tenant.objects.get(id=tenant_id, is_active=True)
        except Exception:
            logger.warning(f'X-Tenant-ID header contains unknown id: {tenant_id}')
            return None

    def _get_tenant_by_slug(self, slug):
        from core.models import Tenant
        try:
            return Tenant.objects.get(slug=slug, is_active=True)
        except Tenant.DoesNotExist:
            logger.warning(f'X-Tenant-Slug header contains unknown slug: {slug}')
            return None

    def _get_tenant_from_user(self, user):
        try:
            return user.membership.tenant
        except Exception:
            return None