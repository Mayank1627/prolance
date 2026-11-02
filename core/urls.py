from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    path('dashboard/', views.dashboard_router_view, name='dashboard'),
    path('dashboard/freelancer/', views.freelancer_dashboard_view, name='freelancer_dashboard'),
    path('dashboard/client/', views.client_dashboard_view, name='client_dashboard'),
]
