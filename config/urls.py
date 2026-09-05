"""
URL configuration for intern_management project.
Damak Municipality Intern Management System (IMS) - Phase 5: Daily Logbook.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views
from interns import views as interns_views
from attendance import views as attendance_views
from logbook import views as logbook_views
from tasks import views as tasks_views

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

    # Phase 3 Core Routes
    path('supervisor/interns/', interns_views.supervisor_my_interns_view, name='supervisor_my_interns'),
    path('supervisor/profile/', interns_views.supervisor_profile_view, name='supervisor_profile'),
    path('intern/internship/', interns_views.intern_my_internship_view, name='intern_my_internship'),
    path('intern/profile/', interns_views.intern_profile_view, name='intern_profile'),
    path('departments/', interns_views.department_list_view, name='department_list'),
    path('departments/create/', interns_views.department_create_view, name='department_create'),
    path('departments/<int:pk>/edit/', interns_views.department_edit_view, name='department_edit'),
    path('departments/<int:pk>/delete/', interns_views.department_delete_view, name='department_delete'),

    # Phase 4 Core Attendance Routes
    path('intern/attendance/', attendance_views.intern_attendance_today_view, name='intern_attendance_today'),
    path('intern/attendance/mark/', attendance_views.intern_mark_present_view, name='intern_mark_present'),
    path('intern/attendance/checkout/', attendance_views.intern_checkout_view, name='intern_checkout'),
    path('intern/attendance/history/', attendance_views.intern_attendance_history_view, name='intern_attendance_history'),
    path('supervisor/attendance/', attendance_views.supervisor_attendance_list_view, name='supervisor_attendance'),
    path('supervisor/attendance/create/', attendance_views.supervisor_attendance_create_view, name='supervisor_attendance_create'),
    path('supervisor/attendance/<int:pk>/edit/', attendance_views.supervisor_attendance_edit_view, name='supervisor_attendance_edit'),

    # Phase 5 Core Logbook Routes (intern)
    path('intern/logbook/', logbook_views.intern_logbook_list_view, name='intern_logbook'),
    path('intern/logbook/create/', logbook_views.intern_log_create_view, name='intern_log_create'),
    path('intern/logbook/<int:pk>/', logbook_views.intern_log_detail_view, name='intern_log_detail'),
    path('intern/logbook/<int:pk>/edit/', logbook_views.intern_log_edit_view, name='intern_log_edit'),

    # Phase 5 Core Logbook Routes (supervisor)
    path('supervisor/logbook/', logbook_views.supervisor_logbook_list_view, name='supervisor_logbook'),
    path('supervisor/logbook/<int:pk>/', logbook_views.supervisor_log_detail_view, name='supervisor_log_detail'),
    path('supervisor/logbook/<int:pk>/approve/', logbook_views.supervisor_log_approve_view, name='supervisor_log_approve'),
    path('supervisor/logbook/<int:pk>/reject/', logbook_views.supervisor_log_reject_view, name='supervisor_log_reject'),

    # Phase 6 Core Tasks Routes (intern)
    path('intern/tasks/', tasks_views.intern_task_list_view, name='intern_task_list'),
    path('intern/tasks/<int:pk>/', tasks_views.intern_task_detail_view, name='intern_task_detail'),
    path('intern/tasks/<int:pk>/update/', tasks_views.intern_task_detail_view, name='intern_task_update'), # detail view handles POST

    # Phase 6 Core Tasks Routes (supervisor)
    path('supervisor/tasks/', tasks_views.supervisor_task_list_view, name='supervisor_task_list'),
    path('supervisor/tasks/create/', tasks_views.supervisor_task_create_view, name='supervisor_task_create'),
    path('supervisor/tasks/<int:pk>/', tasks_views.supervisor_task_detail_view, name='supervisor_task_detail'),
    path('supervisor/tasks/<int:pk>/edit/', tasks_views.supervisor_task_edit_view, name='supervisor_task_edit'),

    # App namespaced routes
    path('accounts/', include('accounts.urls')),
    path('interns/', include('interns.urls')),
    path('attendance/', include('attendance.urls')),
    path('logbook/', include('logbook.urls')),
    path('tasks/', include('tasks.urls')),
    
    # Phase 7 Core Evaluations Routes
    path('evaluations/', include('evaluations.urls')),
    path('documents/', include('documents.urls')),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
