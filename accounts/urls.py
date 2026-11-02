from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('password/change/', views.password_change_view, name='password_change'),
    path('talent/', views.freelancers_list_view, name='freelancers_list'),
    path('talent/<str:username>/', views.freelancer_detail_view, name='freelancer_profile_detail'),
]
