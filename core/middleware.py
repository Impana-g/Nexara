# core/middleware.py

import threading
import logging
from django.http import JsonResponse

logger = logging.getLogger('nexara.core.middleware')

# ─── Thread-local storage ─────────────────────────────────────────────────────
# Stores the current tenant for the duration of each request.
# Safe across concurrent requests because each request runs in its own thread.

_thread_locals = threading.local()


def get_current_tenant():
    """
    Returns the Tenant object for the current request thread.
    Returns None if called outside a request context (e.g. in a Celery task).
    Use set_current_tenant() in Celery tasks to set it manually.
    """
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """
    Manually set the tenant for the current thread.
    Call this at the top of every Celery task that touches tenant-scoped models:

        from core.middleware import set_current_tenant
        from core.models import Tenant

        @app.task
        def my_task(tenant_id):
            tenant = Tenant.objects.get(id=tenant_id)
            set_current_tenant(tenant)
            # now TenantAwareManager filters correctly
    """
    _thread_locals.tenant = tenant


def clear_current_tenant():
    """
    Clears the tenant from thread-local storage.
    Called automatically at the end of every request.
    """
    _thread_locals.tenant = None


# ─── Middleware class ─────────────────────────────────────────────────────────

class TenantMiddleware:
    """
    Resolves the tenant for every incoming request and stores it in
    thread-local state so TenantAwareManager can filter queries automatically.

    Resolution order:
      1. X-Tenant-Slug header  (used by Next.js frontend and internal services)
      2. JWT token sub-claim   (future — when Supabase Auth is wired up)
      3. None                  (unauthenticated or admin requests pass through)

    Placed after AuthenticationMiddleware in MIDDLEWARE so request.user is
    already populated when this runs.
    """

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

        # Always clean up — never let one request's tenant leak into the next
        clear_current_tenant()

        return response

    def _resolve_tenant(self, request):
        """
        Try each resolution strategy in order. Return the first match.
        """
        # Skip tenant resolution for Django admin and health check
        path = request.path_info
        if path.startswith('/admin/') or path == '/health/':
            return None

        # Strategy 1: X-Tenant-Slug header
        slug = request.headers.get('X-Tenant-Slug')
        if slug:
            return self._get_tenant_by_slug(slug)

        # Strategy 2: Authenticated user's membership
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self._get_tenant_from_user(request.user)

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