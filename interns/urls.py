from django.urls import path
from . import views

app_name = 'interns'

urlpatterns = [
    path('', views.intern_list_placeholder, name='list'),
]
