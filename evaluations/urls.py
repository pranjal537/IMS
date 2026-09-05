from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    # Supervisor URLs
    path('supervisor/evaluations/', views.supervisor_evaluation_list, name='supervisor_evaluation_list'),
    path('supervisor/evaluations/<int:pk>/', views.supervisor_evaluation_detail, name='supervisor_evaluation_detail'),
    path('supervisor/evaluations/create/<int:internship_id>/', views.supervisor_evaluation_create, name='supervisor_evaluation_create'),
    path('supervisor/evaluations/<int:pk>/edit/', views.supervisor_evaluation_edit, name='supervisor_evaluation_edit'),
    
    # Intern URLs
    path('intern/evaluation/', views.intern_evaluation_detail, name='intern_evaluation_detail'),
    path('intern/progress/', views.intern_progress, name='intern_progress'),
]
