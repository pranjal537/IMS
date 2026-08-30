from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('supervisor/dashboard/', views.supervisor_dashboard_view, name='supervisor_dashboard'),
    path('intern/dashboard/', views.intern_dashboard_view, name='intern_dashboard'),
    path('password/change/', views.password_change_view, name='password_change'),
    path('health/', views.health_view, name='health_check'),
]
