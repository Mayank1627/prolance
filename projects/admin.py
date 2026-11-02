from django.contrib import admin
from .models import Category, Skill, Project, SavedProject

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_theme', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'category', 'status', 'budget_min', 'budget_max', 'hired_freelancer', 'created_at')
    list_filter = ('status', 'category', 'project_type')
    search_fields = ('title', 'description', 'client__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('required_skills',)

@admin.register(SavedProject)
class SavedProjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'created_at')
    search_fields = ('user__username', 'project__title')
