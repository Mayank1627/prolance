from django.urls import path
from . import views

app_name = 'workspace'

urlpatterns = [
    path('<slug:slug>/', views.workspace_room_view, name='room'),
    path('<slug:slug>/message/', views.send_message_view, name='send_message'),
    path('<slug:slug>/deliverable/submit/', views.submit_deliverable_view, name='submit_deliverable'),
    path('<slug:slug>/deliverable/<int:deliverable_id>/review/', views.review_deliverable_view, name='review_deliverable'),
    path('<slug:slug>/complete/', views.complete_project_view, name='complete_project'),
]

