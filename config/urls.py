"""
URL configuration for intern_management project.
Damak Municipality Intern Management System (IMS) - Phase 2: Auth & Roles.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core routes (mounted directly at root for clean URLs)
    path('', accounts_views.home_view, name='home'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('dashboard/', accounts_views.dashboard_redirect_view, name='dashboard_redirect'),
    path('supervisor/dashboard/', accounts_views.supervisor_dashboard_view, name='supervisor_dashboard'),
    path('intern/dashboard/', accounts_views.intern_dashboard_view, name='intern_dashboard'),
    path('password-change/', accounts_views.password_change_view, name='password_change'),
    path('password/change/', accounts_views.password_change_view),
    path('health/', accounts_views.health_view, name='health_check'),

    # App namespaced routes
    path('accounts/', include('accounts.urls')),
    path('interns/', include('interns.urls')),
    path('attendance/', include('attendance.urls')),
    path('logbook/', include('logbook.urls')),
    path('tasks/', include('tasks.urls')),
    path('evaluations/', include('evaluations.urls')),
    path('documents/', include('documents.urls')),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
