from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Intern routes
    path('intern/attendance/', views.intern_attendance_today_view, name='intern_today'),
    path('intern/attendance/mark/', views.intern_mark_present_view, name='intern_mark_present'),
    path('intern/attendance/checkout/', views.intern_checkout_view, name='intern_checkout'),
    path('intern/attendance/history/', views.intern_attendance_history_view, name='intern_history'),

    # Supervisor routes
    path('supervisor/attendance/', views.supervisor_attendance_list_view, name='supervisor_list'),
    path('supervisor/attendance/create/', views.supervisor_attendance_create_view, name='supervisor_create'),
    path('supervisor/attendance/<int:pk>/edit/', views.supervisor_attendance_edit_view, name='supervisor_edit'),
]
