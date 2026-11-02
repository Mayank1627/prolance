from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('project/<slug:slug>/create/', views.create_review_view, name='create_review'),
    path('report/', views.report_content_view, name='report_content'),
]
