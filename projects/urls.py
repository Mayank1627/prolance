from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_browse_view, name='browse'),
    path('create/', views.project_create_view, name='create'),
    path('saved/', views.saved_projects_list_view, name='saved_list'),
    path('<slug:slug>/', views.project_detail_view, name='detail'),
    path('<slug:slug>/edit/', views.project_edit_view, name='edit'),
    path('<slug:slug>/close/', views.project_close_view, name='close'),
    path('<int:project_id>/toggle-save/', views.toggle_save_project_view, name='toggle_save'),
]
