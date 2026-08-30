"""
Role-based access control decorators for Damak Municipality IMS.

Usage:
    @login_required
    @supervisor_required
    def my_supervisor_view(request): ...

    @login_required
    @intern_required
    def my_intern_view(request): ...
"""

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def supervisor_required(view_func):
    """
    Decorator that requires the authenticated user to have the SUPERVISOR role.
    Unauthenticated users are redirected to login.
    Authenticated interns receive a 403 Forbidden response.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        if not request.user.is_supervisor:
            return HttpResponseForbidden(
                "<h2>403 – Access Denied</h2>"
                "<p>You do not have permission to access this page. "
                "This area is reserved for Supervisors only.</p>"
                "<p><a href='/'>Return to Home</a></p>"
            )
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def intern_required(view_func):
    """
    Decorator that requires the authenticated user to have the INTERN role.
    Unauthenticated users are redirected to login.
    Authenticated supervisors receive a 403 Forbidden response.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        if not request.user.is_intern:
            return HttpResponseForbidden(
                "<h2>403 – Access Denied</h2>"
                "<p>You do not have permission to access this page. "
                "This area is reserved for Interns only.</p>"
                "<p><a href='/'>Return to Home</a></p>"
            )
        return view_func(request, *args, **kwargs)
    return _wrapped_view
