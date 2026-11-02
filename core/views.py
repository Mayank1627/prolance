from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator

from projects.models import Project, Category, SavedProject
from accounts.models import User, FreelancerProfile
from proposals.models import Proposal
from reviews.models import Review

def landing_view(request):
    """Dynamic public landing page with real database metrics."""
    # Featured open projects
    featured_projects = Project.objects.filter(status=Project.STATUS_OPEN).select_related('client', 'category').prefetch_related('required_skills')[:6]
    
    # Categories with live project counts
    categories = Category.objects.annotate(
        active_project_count=Count('projects', filter=Q(projects__status=Project.STATUS_OPEN))
    ).order_by('-active_project_count')[:6]

    # Real platform metrics
    total_projects = Project.objects.count()
    total_freelancers = User.objects.filter(role=User.ROLE_FREELANCER).count()
    total_clients = User.objects.filter(role=User.ROLE_CLIENT).count()
    total_reviews = Review.objects.count()

    # Featured top-rated freelancers
    featured_freelancers = User.objects.filter(
        role=User.ROLE_FREELANCER,
        freelancer_profile__is_available=True
    ).select_related('freelancer_profile')[:4]

    return render(request, 'core/landing.html', {
        'featured_projects': featured_projects,
        'categories': categories,
        'total_projects': total_projects,
        'total_freelancers': total_freelancers,
        'total_clients': total_clients,
        'total_reviews': total_reviews,
        'featured_freelancers': featured_freelancers,
    })


def how_it_works_view(request):
    """Explains the Prolance methodology and milestone delivery workflow."""
    return render(request, 'core/how_it_works.html')


@login_required
def dashboard_router_view(request):
    """Directs authenticated users to their specific dashboard based on role."""
    if request.user.is_client_user():
        return redirect('core:client_dashboard')
    elif request.user.is_freelancer_user():
        return redirect('core:freelancer_dashboard')
    elif request.user.is_staff or request.user.is_superuser:
        return redirect('core:client_dashboard')
    return redirect('projects:browse')


@login_required
def freelancer_dashboard_view(request):
    """Dashboard specifically for freelancers with real database metrics."""
    if not request.user.is_freelancer_user() and not request.user.is_superuser:
        return redirect('core:client_dashboard')

    user = request.user
    profile, _ = FreelancerProfile.objects.get_or_create(user=user)

    # Proposals breakdown
    proposals = Proposal.objects.filter(freelancer=user).select_related('project', 'project__client')
    pending_proposals_count = proposals.filter(status=Proposal.STATUS_PENDING).count()
    accepted_proposals_count = proposals.filter(status=Proposal.STATUS_ACCEPTED).count()
    rejected_proposals_count = proposals.filter(status=Proposal.STATUS_REJECTED).count()

    # Active projects (In Progress or Under Review)
    active_projects = Project.objects.filter(
        hired_freelancer=user,
        status__in=[Project.STATUS_IN_PROGRESS, Project.STATUS_REVIEW]
    ).select_related('client', 'category')

    # Completed projects
    completed_projects = Project.objects.filter(
        hired_freelancer=user,
        status=Project.STATUS_COMPLETED
    ).select_related('client', 'category')

    # Saved projects count
    saved_count = SavedProject.objects.filter(user=user).count()

    # Calculate profile completeness percentage
    completeness = 25  # base user created
    if profile.headline and len(profile.headline) > 5:
        completeness += 20
    if profile.bio and len(profile.bio) > 20:
        completeness += 20
    if profile.hourly_rate:
        completeness += 15
    if profile.portfolio_url or profile.github_url:
        completeness += 10
    if profile.avatar:
        completeness += 10

    # Recent proposals slice
    recent_proposals = proposals.order_by('-created_at')[:5]

    return render(request, 'core/freelancer_dashboard.html', {
        'profile': profile,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'recent_proposals': recent_proposals,
        'pending_count': pending_proposals_count,
        'accepted_count': accepted_proposals_count,
        'rejected_count': rejected_proposals_count,
        'saved_count': saved_count,
        'completeness': completeness,
    })


@login_required
def client_dashboard_view(request):
    """Dashboard specifically for clients with real database metrics."""
    if not request.user.is_client_user() and not request.user.is_superuser:
        return redirect('core:freelancer_dashboard')

    user = request.user
    posted_projects = Project.objects.filter(client=user).select_related('category', 'hired_freelancer').annotate(
        proposal_count_annotated=Count('proposals')
    ).order_by('-created_at')

    open_count = posted_projects.filter(status=Project.STATUS_OPEN).count()
    active_count = posted_projects.filter(status__in=[Project.STATUS_IN_PROGRESS, Project.STATUS_REVIEW]).count()
    completed_count = posted_projects.filter(status=Project.STATUS_COMPLETED).count()

    # Recent proposals received across all client projects
    recent_proposals = Proposal.objects.filter(
        project__client=user
    ).select_related('project', 'freelancer', 'freelancer__freelancer_profile').order_by('-created_at')[:6]

    return render(request, 'core/client_dashboard.html', {
        'posted_projects': posted_projects,
        'open_count': open_count,
        'active_count': active_count,
        'completed_count': completed_count,
        'recent_proposals': recent_proposals,
    })
