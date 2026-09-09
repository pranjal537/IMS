from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list_view, name='document_list'),
    path('upload/', views.document_upload_view, name='document_upload'),
    path('supervisor/upload/<int:intern_id>/', views.document_upload_view, name='supervisor_document_upload'),
    path('<int:pk>/download/', views.document_download_view, name='document_download'),
    path('<int:pk>/delete/', views.document_delete_view, name='document_delete'),
]
