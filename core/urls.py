# core/urls.py

from django.urls import path
from core import views

urlpatterns = [
    # Health
    path('health/',              views.health_check,          name='health-check'),

    # Auth — HTML Form Views (pages)
    path('register/',            views.register_form_view,    name='auth-register-form'),
    path('login/',               views.login_form_view,       name='auth-login-form'),
    path('dashboard/',           views.dashboard_view,        name='dashboard'),

    # Auth — API Views (JSON endpoints)
    path('api/auth/register/',   views.register_view,         name='auth-register'),
    path('api/auth/login/',      views.login_view,            name='auth-login'),
    path('api/auth/logout/',     views.logout_view,           name='auth-logout'),
    path('api/auth/me/',         views.me_view,               name='auth-me'),

    # Tenants
    path('api/tenants/',                         views.TenantListCreateView.as_view(), name='tenant-list'),
    path('api/tenants/<slug:slug>/',             views.TenantDetailView.as_view(),     name='tenant-detail'),
    path('api/tenants/<slug:slug>/members/',     views.MembershipListView.as_view(),   name='tenant-members'),
]