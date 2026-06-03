"""
URL configuration for nexara_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# nexara_platform/urls.py

# nexara_platform/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',   admin.site.urls),

    # Core: auth, tenants, users
    path('',         include('core.urls')),

    # Engine: workflow execution, HITL, SSE
    path('',         include('engine.urls')),

    # ── Domain APIs ──────────────────────────────────────────────────────────

    path('api/hr/',             include('domains.hr.urls')),
    path('api/it/',             include('domains.it.urls')),
    path('api/healthcare/',     include('domains.healthcare.urls')),
    path('api/education/',      include('domains.education.urls')),
    path('api/legal/',          include('domains.legal.urls')),
    path('api/insurance/',      include('domains.insurance.urls')),
    path('api/energy/',         include('domains.energy.urls')),
    path('api/government/',     include('domains.government.urls')),
    path('api/logistics/',      include('domains.logistics.urls')),
    path('api/manufacturing/',  include('domains.manufacturing.urls')),
    path('api/retail/',         include('domains.retail.urls')),
    path('api/telecom/',        include('domains.telecom.urls')),
    path('api/cybersecurity/',  include('domains.cybersecurity.urls')),
    # MCP Server
    path('mcp/',                include('mcp.urls')),
]