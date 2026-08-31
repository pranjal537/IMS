from django.urls import path
from . import views

app_name = 'logbook'

urlpatterns = [
    # ── Intern Logbook ─────────────────────────────────────────────────────
    path('intern/', views.intern_logbook_list_view, name='intern_list'),
    path('intern/create/', views.intern_log_create_view, name='intern_create'),
    path('intern/<int:pk>/', views.intern_log_detail_view, name='intern_detail'),
    path('intern/<int:pk>/edit/', views.intern_log_edit_view, name='intern_edit'),

    # ── Supervisor Logbook ─────────────────────────────────────────────────
    path('supervisor/', views.supervisor_logbook_list_view, name='supervisor_list'),
    path('supervisor/<int:pk>/', views.supervisor_log_detail_view, name='supervisor_detail'),
    path('supervisor/<int:pk>/approve/', views.supervisor_log_approve_view, name='supervisor_approve'),
    path('supervisor/<int:pk>/reject/', views.supervisor_log_reject_view, name='supervisor_reject'),
]
