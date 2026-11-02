from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .models import Project, Category, Skill, SavedProject
from .forms import ProjectForm
from proposals.models import Proposal

def project_browse_view(request):
    """Search, filter, and discover open marketplace projects."""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    skill_slug = request.GET.get('skill', '').strip()
    project_type = request.GET.get('type', '').strip()
    min_budget = request.GET.get('min_budget', '').strip()
    max_budget = request.GET.get('max_budget', '').strip()
    sort = request.GET.get('sort', 'newest')

    projects = Project.objects.filter(status=Project.STATUS_OPEN).select_related('client', 'category').prefetch_related('required_skills')

    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__name__icontains=query)
        ).distinct()

    if category_slug:
        projects = projects.filter(category__slug=category_slug)

    if skill_slug:
        projects = projects.filter(required_skills__slug=skill_slug)

    if project_type in [Project.TYPE_FIXED, Project.TYPE_HOURLY]:
        projects = projects.filter(project_type=project_type)

    if min_budget:
        try:
            projects = projects.filter(budget_max__gte=float(min_budget))
        except ValueError:
            pass

    if max_budget:
        try:
            projects = projects.filter(budget_min__lte=float(max_budget))
        except ValueError:
            pass

    # Sorting
    if sort == 'budget_high':
        projects = projects.order_by('-budget_max', '-created_at')
    elif sort == 'budget_low':
        projects = projects.order_by('budget_min', '-created_at')
    elif sort == 'deadline':
        projects = projects.order_by('deadline', '-created_at')
    else:
        projects = projects.order_by('-created_at')

    categories = Category.objects.all()
    skills = Skill.objects.all()

    paginator = Paginator(projects, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'projects/browse.html', {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
        'categories': categories,
        'skills': skills,
        'selected_category': category_slug,
        'selected_skill': skill_slug,
        'selected_type': project_type,
        'query': query,
        'sort': sort,
        'min_budget': min_budget,
        'max_budget': max_budget,
    })


def project_detail_view(request, slug):
    project = get_object_or_404(
        Project.objects.select_related('client', 'category', 'hired_freelancer').prefetch_related('required_skills'),
        slug=slug
    )

    user_proposal = None
    is_saved = False

    if request.user.is_authenticated:
        if request.user.is_freelancer_user():
            user_proposal = Proposal.objects.filter(project=project, freelancer=request.user).first()
            is_saved = SavedProject.objects.filter(user=request.user, project=project).exists()

    # Related projects in same category
    related_projects = Project.objects.filter(
        category=project.category,
        status=Project.STATUS_OPEN
    ).exclude(pk=project.pk)[:3]

    return render(request, 'projects/detail.html', {
        'project': project,
        'user_proposal': user_proposal,
        'is_saved': is_saved,
        'related_projects': related_projects,
    })


@login_required
def project_create_view(request):
    """Only clients can publish new projects."""
    if not request.user.is_client_user():
        messages.error(request, "Only registered Client accounts may publish project specifications.")
        return redirect('projects:browse')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.status = Project.STATUS_OPEN
            project.save()
            form.save_m2m()  # save required skills
            messages.success(request, f"Project '{project.title}' is now live on the marketplace!")
            return redirect('projects:detail', slug=project.slug)
        else:
            messages.error(request, "Please review the form errors before publishing.")
    else:
        form = ProjectForm()

    return render(request, 'projects/form.html', {
        'form': form,
        'page_title': 'Publish New Project Listing',
        'is_edit': False,
    })


@login_required
def project_edit_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not project.is_owner(request.user) and not request.user.is_superuser:
        raise PermissionDenied("You do not hold permissions to edit this project.")

    if project.status in [Project.STATUS_COMPLETED, Project.STATUS_CLOSED]:
        messages.warning(request, "Completed or closed projects cannot be edited.")
        return redirect('projects:detail', slug=project.slug)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project details updated successfully.")
            return redirect('projects:detail', slug=project.slug)
        else:
            messages.error(request, "Please resolve the highlighted errors.")
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/form.html', {
        'form': form,
        'project': project,
        'page_title': f"Edit Project: {project.title}",
        'is_edit': True,
    })


@login_required
def project_close_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not project.is_owner(request.user) and not request.user.is_superuser:
        raise PermissionDenied("You do not hold permission to alter this project status.")

    if request.method == 'POST':
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=['status'])
        messages.success(request, f"Project '{project.title}' has been closed.")
        return redirect('core:client_dashboard')

    return render(request, 'projects/confirm_close.html', {'project': project})


@login_required
def toggle_save_project_view(request, project_id):
    if not request.user.is_freelancer_user():
        messages.error(request, "Only freelancers can bookmark projects for later review.")
        return redirect('projects:browse')

    project = get_object_or_404(Project, id=project_id)
    saved_obj, created = SavedProject.objects.get_or_create(user=request.user, project=project)

    if not created:
        saved_obj.delete()
        messages.info(request, f"Removed '{project.title}' from your saved bookmarks.")
    else:
        messages.success(request, f"Saved '{project.title}' to your bookmarks.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('projects:detail', slug=project.slug)


@login_required
def saved_projects_list_view(request):
    if not request.user.is_freelancer_user():
        messages.error(request, "This dashboard view is reserved for freelancer accounts.")
        return redirect('core:dashboard')

    saved_items = SavedProject.objects.filter(user=request.user).select_related('project', 'project__client', 'project__category')
    
    paginator = Paginator(saved_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'projects/saved_list.html', {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
    })
