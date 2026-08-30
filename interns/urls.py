from django.urls import path
from . import views

app_name = 'interns'

urlpatterns = [
    # Supervisor routes
    path('supervisor/interns/', views.supervisor_my_interns_view, name='supervisor_my_interns'),
    path('supervisor/profile/', views.supervisor_profile_view, name='supervisor_profile'),

    # Intern routes
    path('intern/internship/', views.intern_my_internship_view, name='intern_my_internship'),
    path('intern/profile/', views.intern_profile_view, name='intern_profile'),

    # Department Management routes (Staff/Admin)
    path('departments/', views.department_list_view, name='department_list'),
    path('departments/create/', views.department_create_view, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit_view, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete_view, name='department_delete'),
]
