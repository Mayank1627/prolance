from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.db import transaction

from .models import ProjectDeliverable, ProjectMessage
from .forms import DeliverableSubmissionForm, DeliverableReviewForm, ProjectMessageForm
from projects.models import Project
from notifications.models import Notification
from reviews.models import Review

def verify_workspace_participant(user, project):
    """Enforces strict server-side authorization for workspace rooms."""
    if user.is_superuser or user.is_staff:
        return True
    return user == project.client or (project.hired_freelancer and user == project.hired_freelancer)


@login_required
def workspace_room_view(request, slug):
    project = get_object_or_404(
        Project.objects.select_related('client', 'hired_freelancer', 'category'),
        slug=slug
    )

    if not verify_workspace_participant(request.user, project):
        raise PermissionDenied("You are not an authorized participant in this project workspace.")

    # Mark messages from the counterpart as read
    ProjectMessage.objects.filter(project=project).exclude(sender=request.user).update(is_read=True)

    deliverables = project.deliverables.select_related('submitted_by').order_by('-created_at')
    chat_messages = project.messages.select_related('sender').order_by('created_at')

    # Check review status for participants
    has_reviewed = False
    if project.status == Project.STATUS_COMPLETED:
        other_party = project.hired_freelancer if request.user == project.client else project.client
        has_reviewed = Review.objects.filter(project=project, reviewer=request.user, reviewee=other_party).exists()

    deliverable_form = DeliverableSubmissionForm()
    message_form = ProjectMessageForm()

    return render(request, 'workspace/room.html', {
        'project': project,
        'deliverables': deliverables,
        'chat_messages': chat_messages,
        'deliverable_form': deliverable_form,
        'message_form': message_form,
        'has_reviewed': has_reviewed,
        'is_client': request.user == project.client,
        'is_freelancer': request.user == project.hired_freelancer,
    })


@login_required
def send_message_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not verify_workspace_participant(request.user, project):
        raise PermissionDenied("You cannot send messages to this project room.")

    if request.method == 'POST':
        form = ProjectMessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.project = project
            msg.sender = request.user
            msg.save()

            # Determine counterpart recipient
            recipient = project.hired_freelancer if request.user == project.client else project.client
            if recipient:
                Notification.objects.create(
                    recipient=recipient,
                    title=f"New Message from {request.user.get_display_name()}",
                    message=f"'{request.user.get_display_name()}' posted a message in '{project.title}'.",
                    url=f"/workspace/{project.slug}/#chat",
                    category='message'
                )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'sender': msg.sender.get_display_name(),
                    'message': msg.message,
                    'created_at': msg.created_at.strftime('%b %d, %H:%M'),
                })

            messages.success(request, "Message sent.")
        else:
            messages.error(request, "Could not send empty message.")

    return redirect('workspace:room', slug=project.slug)


@login_required
def submit_deliverable_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if request.user != project.hired_freelancer and not request.user.is_superuser:
        raise PermissionDenied("Only the hired freelancer may submit deliverables.")

    if project.status in [Project.STATUS_COMPLETED, Project.STATUS_CLOSED]:
        messages.warning(request, "Cannot submit deliverables to completed or closed projects.")
        return redirect('workspace:room', slug=project.slug)

    if request.method == 'POST':
        form = DeliverableSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            deliverable = form.save(commit=False)
            deliverable.project = project
            deliverable.submitted_by = request.user
            deliverable.status = ProjectDeliverable.STATUS_SUBMITTED
            deliverable.save()

            # Automatically transition project to review status
            project.status = Project.STATUS_REVIEW
            project.save(update_fields=['status', 'updated_at'])

            Notification.objects.create(
                recipient=project.client,
                title="Deliverable Submitted for Review",
                message=f"{request.user.get_display_name()} has submitted '{deliverable.title}' for your inspection.",
                url=f"/workspace/{project.slug}/#deliverables",
                category='deliverable'
            )

            messages.success(request, f"Deliverable '{deliverable.title}' has been submitted for client review.")
        else:
            messages.error(request, "Please review your deliverable submission fields.")

    return redirect('workspace:room', slug=project.slug)


@login_required
def review_deliverable_view(request, slug, deliverable_id):
    project = get_object_or_404(Project, slug=slug)
    deliverable = get_object_or_404(ProjectDeliverable, id=deliverable_id, project=project)

    if request.user != project.client and not request.user.is_superuser:
        raise PermissionDenied("Only the project client can review deliverables.")

    if request.method == 'POST':
        status = request.POST.get('status')
        feedback = request.POST.get('client_feedback', '').strip()

        if status in [ProjectDeliverable.STATUS_APPROVED, ProjectDeliverable.STATUS_REVISION]:
            deliverable.status = status
            deliverable.client_feedback = feedback
            deliverable.save(update_fields=['status', 'client_feedback', 'updated_at'])

            if status == ProjectDeliverable.STATUS_APPROVED:
                messages.success(request, f"Deliverable '{deliverable.title}' marked as Approved.")
                Notification.objects.create(
                    recipient=project.hired_freelancer,
                    title="Deliverable Approved!",
                    message=f"The client approved '{deliverable.title}'.",
                    url=f"/workspace/{project.slug}/",
                    category='deliverable'
                )
            else:
                messages.info(request, f"Requested revisions for '{deliverable.title}'.")
                Notification.objects.create(
                    recipient=project.hired_freelancer,
                    title="Revisions Requested",
                    message=f"The client requested revisions for '{deliverable.title}': {feedback[:80]}",
                    url=f"/workspace/{project.slug}/",
                    category='deliverable'
                )

    return redirect('workspace:room', slug=project.slug)


@login_required
def complete_project_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if request.user != project.client and not request.user.is_superuser:
        raise PermissionDenied("Only the client owner may sign off on project completion.")

    if project.status == Project.STATUS_COMPLETED:
        messages.info(request, "This project has already been marked completed.")
        return redirect('workspace:room', slug=project.slug)

    if request.method == 'POST':
        project.status = Project.STATUS_COMPLETED
        project.save(update_fields=['status', 'updated_at'])

        if project.hired_freelancer:
            Notification.objects.create(
                recipient=project.hired_freelancer,
                title="Project Successfully Completed!",
                message=f"The client has signed off and completed '{project.title}'. Please leave your feedback review.",
                url=f"/workspace/{project.slug}/",
                category='system'
            )

        messages.success(request, f"Project '{project.title}' is officially completed! Please leave a review for your freelancer.")
        return redirect('reviews:create_review', slug=project.slug)

    return render(request, 'workspace/confirm_complete.html', {'project': project})
