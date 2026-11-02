from django.urls import path
from . import views

app_name = 'proposals'

urlpatterns = [
    path('apply/<slug:slug>/', views.submit_proposal_view, name='submit'),
    path('withdraw/<int:proposal_id>/', views.withdraw_proposal_view, name='withdraw'),
    path('project/<slug:slug>/', views.project_proposals_view, name='project_proposals'),
    path('<int:proposal_id>/accept/', views.accept_proposal_view, name='accept'),
    path('<int:proposal_id>/reject/', views.reject_proposal_view, name='reject'),
]
