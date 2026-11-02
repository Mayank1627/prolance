from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import Review, Report
from .forms import ReviewForm, ReportForm
from projects.models import Project
from accounts.models import User
from notifications.models import Notification

@login_required
def create_review_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    # Must be completed
    if project.status != Project.STATUS_COMPLETED:
        messages.error(request, "Reviews can only be submitted after the project has been officially completed.")
        return redirect('workspace:room', slug=project.slug)

    # Must be either client or hired freelancer
    if request.user == project.client:
        reviewee = project.hired_freelancer
        reviewee_role = "Freelancer"
    elif request.user == project.hired_freelancer:
        reviewee = project.client
        reviewee_role = "Client"
    else:
        raise PermissionDenied("Only participants in this completed project may leave a review.")

    # Check if review already exists
    existing_review = Review.objects.filter(project=project, reviewer=request.user, reviewee=reviewee).first()
    if existing_review:
        messages.info(request, "You have already submitted your review for this project engagement.")
        return redirect('workspace:room', slug=project.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = project
            review.reviewer = request.user
            review.reviewee = reviewee
            review.save()

            # Create notification
            Notification.objects.create(
                recipient=reviewee,
                title="New Review Received!",
                message=f"{request.user.get_display_name()} left you a {review.rating}-star review for '{project.title}'.",
                url=f"/workspace/{project.slug}/",
                category='review'
            )

            messages.success(request, f"Thank you! Your review for {reviewee.get_display_name()} has been published.")
            return redirect('workspace:room', slug=project.slug)
        else:
            messages.error(request, "Please address the errors in your review submission.")
    else:
        form = ReviewForm()

    return render(request, 'reviews/create_review.html', {
        'form': form,
        'project': project,
        'reviewee': reviewee,
        'reviewee_role': reviewee_role,
    })


@login_required
def report_content_view(request):
    project_id = request.GET.get('project_id')
    user_id = request.GET.get('user_id')

    project = Project.objects.filter(id=project_id).first() if project_id else None
    reported_user = User.objects.filter(id=user_id).first() if user_id else None

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.project = project
            report.reported_user = reported_user
            report.save()

            messages.success(request, "Your report has been logged with Trust & Safety. Administrators will inspect the issue.")
            return redirect('core:landing')
    else:
        form = ReportForm()

    return render(request, 'reviews/report_form.html', {
        'form': form,
        'project': project,
        'reported_user': reported_user,
    })
