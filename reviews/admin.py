from django.contrib import admin
from .models import Review, Report

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('project', 'reviewer', 'reviewee', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('project__title', 'reviewer__username', 'reviewee__username', 'feedback')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reason', 'reporter', 'project', 'reported_user', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('reason', 'details', 'reporter__username')
