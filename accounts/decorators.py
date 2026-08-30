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
from django.shortcuts import redirect, render
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
            return render(request, '403.html', status=403)
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
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
