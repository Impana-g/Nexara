# core/auth_decorators.py
"""
Authentication decorators for protecting views
"""

from functools import wraps
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework import status


def login_required_view(view_func):
    """
    Decorator to ensure user is authenticated for function-based views.
    Redirects to login page if user is not authenticated.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth-login-form')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_required_api(view_func):
    """
    Decorator to ensure user is authenticated for API views.
    Returns 401 Unauthorized if user is not authenticated.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return view_func(request, *args, **kwargs)
    return wrapper
