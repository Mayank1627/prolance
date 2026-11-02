from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q, Avg

from .models import User, FreelancerProfile, ClientProfile
from .forms import UserRegistrationForm, UserLoginForm, FreelancerProfileForm, ClientProfileForm
from projects.models import Skill, Project
from reviews.models import Review

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()

                # Automatically create role-specific profile
                if user.role == User.ROLE_FREELANCER:
                    FreelancerProfile.objects.create(
                        user=user,
                        headline="Professional Freelancer",
                        bio=f"Hello! I am {user.get_display_name()}. Welcome to my Prolance profile."
                    )
                else:
                    ClientProfile.objects.create(
                        user=user,
                        company_name=user.get_display_name(),
                        bio=f"Client organization represented by {user.get_display_name()}."
                    )

                # Authenticate and login with session
                login(request, user)
                messages.success(request, f"Welcome to Prolance, {user.get_display_name()}! Your account has been established.")
                return redirect('core:dashboard')
        else:
            messages.error(request, "Please correct the issues indicated in the form below.")
    else:
        initial_role = request.GET.get('role', User.ROLE_FREELANCER)
        form = UserRegistrationForm(initial={'role': initial_role})

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_display_name()}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard')
        else:
            messages.error(request, "Invalid username/email or password credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been safely signed out.")
        return redirect('core:landing')
    return redirect('core:landing')


@login_required
def edit_profile_view(request):
    user = request.user

    if user.is_freelancer_user():
        profile, _ = FreelancerProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            form = FreelancerProfileForm(request.POST, request.FILES, instance=profile)
            full_name = request.POST.get('full_name', '').strip()
            if form.is_valid():
                profile = form.save()
                if full_name:
                    user.full_name = full_name
                    user.save(update_fields=['full_name'])
                # Handle skills association
                selected_skills = form.cleaned_data.get('skills')
                # Optional: sync skills
                messages.success(request, "Your freelancer profile has been updated.")
                return redirect('accounts:edit_profile')
            else:
                messages.error(request, "Please resolve the errors highlighted below.")
        else:
            form = FreelancerProfileForm(instance=profile)
    else:
        profile, _ = ClientProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            form = ClientProfileForm(request.POST, request.FILES, instance=profile)
            full_name = request.POST.get('full_name', '').strip()
            if form.is_valid():
                form.save()
                if full_name:
                    user.full_name = full_name
                    user.save(update_fields=['full_name'])
                messages.success(request, "Your client organization profile has been updated.")
                return redirect('accounts:edit_profile')
            else:
                messages.error(request, "Please resolve the errors highlighted below.")
        else:
            form = ClientProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'profile': profile,
    })


def freelancer_detail_view(request, username):
    freelancer = get_object_or_404(User, username=username, role=User.ROLE_FREELANCER)
    profile, _ = FreelancerProfile.objects.get_or_create(user=freelancer)
    
    # Real reviews received
    reviews = Review.objects.filter(reviewee=freelancer).select_related('reviewer', 'project')
    
    # Completed projects assigned to this freelancer
    completed_projects = Project.objects.filter(
        hired_freelancer=freelancer,
        status=Project.STATUS_COMPLETED
    ).select_related('client', 'category')

    return render(request, 'accounts/freelancer_detail.html', {
        'freelancer': freelancer,
        'profile': profile,
        'reviews': reviews,
        'completed_projects': completed_projects,
    })


def freelancers_list_view(request):
    """Talent directory with skill and query filtering."""
    query = request.GET.get('q', '').strip()
    skill_slug = request.GET.get('skill', '').strip()

    freelancers = User.objects.filter(role=User.ROLE_FREELANCER, is_active=True).select_related('freelancer_profile')

    if query:
        freelancers = freelancers.filter(
            Q(full_name__icontains=query) |
            Q(username__icontains=query) |
            Q(freelancer_profile__headline__icontains=query) |
            Q(freelancer_profile__bio__icontains=query)
        )

    skills = Skill.objects.all()

    paginator = Paginator(freelancers.order_by('-date_joined'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/freelancers_list.html', {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
        'skills': skills,
        'query': query,
        'skill_slug': skill_slug,
    })


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your account password was successfully updated.")
            return redirect('accounts:edit_profile')
        else:
            messages.error(request, "Please fix the password errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})
