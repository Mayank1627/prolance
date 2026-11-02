from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FreelancerProfile, ClientProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'full_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Prolance Attributes', {'fields': ('role', 'full_name', 'is_verified')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Prolance Attributes', {'fields': ('role', 'full_name', 'email')}),
    )

@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'hourly_rate', 'experience_years', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('user__username', 'user__full_name', 'headline')

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'industry', 'location')
    search_fields = ('user__username', 'company_name', 'industry')
