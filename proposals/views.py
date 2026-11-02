from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied

from .models import Proposal
from .forms import ProposalSubmissionForm
from projects.models import Project
from notifications.models import Notification

@login_required
def submit_proposal_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not request.user.is_freelancer_user():
        messages.error(request, "Only registered Freelancers may submit project proposals.")
        return redirect('projects:detail', slug=project.slug)

    if project.client == request.user:
        messages.error(request, "You cannot submit a proposal to a project you published.")
        return redirect('projects:detail', slug=project.slug)

    if project.status != Project.STATUS_OPEN:
        messages.warning(request, "This project is no longer accepting new proposals.")
        return redirect('projects:detail', slug=project.slug)

    existing = Proposal.objects.filter(project=project, freelancer=request.user).first()
    if existing:
        messages.info(request, "You have already submitted a proposal for this project.")
        return redirect('projects:detail', slug=project.slug)

    if request.method == 'POST':
        form = ProposalSubmissionForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.project = project
            proposal.freelancer = request.user
            proposal.status = Proposal.STATUS_PENDING
            proposal.save()

            # Create notification for client
            Notification.objects.create(
                recipient=project.client,
                title="New Proposal Received",
                message=f"{request.user.get_display_name()} submitted a ${proposal.proposed_budget} proposal for '{project.title}'.",
                url=f"/proposals/project/{project.slug}/",
                category='proposal'
            )

            messages.success(request, f"Your proposal for '${proposal.proposed_budget}' was successfully delivered to the client!")
            return redirect('projects:detail', slug=project.slug)
        else:
            messages.error(request, "Please address the errors in your proposal.")
    else:
        # Pre-fill proposed budget with project budget_min or average
        form = ProposalSubmissionForm(initial={
            'proposed_budget': project.budget_min,
            'estimated_days': 10
        })

    return render(request, 'proposals/submit.html', {
        'form': form,
        'project': project,
    })


@login_required
def withdraw_proposal_view(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id, freelancer=request.user)

    if proposal.status != Proposal.STATUS_PENDING:
        messages.error(request, "Only pending proposals can be withdrawn.")
        return redirect('projects:detail', slug=proposal.project.slug)

    if request.method == 'POST':
        proposal.status = Proposal.STATUS_WITHDRAWN
        proposal.save(update_fields=['status'])
        messages.info(request, "Your proposal has been withdrawn.")

    return redirect('projects:detail', slug=proposal.project.slug)


@login_required
def project_proposals_view(request, slug):
    """Client view to compare and evaluate all received proposals for their project."""
    project = get_object_or_404(Project, slug=slug)

    if not project.is_owner(request.user) and not request.user.is_superuser:
        raise PermissionDenied("You do not hold permissions to inspect proposals for this project.")

    proposals = project.proposals.select_related('freelancer', 'freelancer__freelancer_profile').order_by('-created_at')

    return render(request, 'proposals/client_proposals_list.html', {
        'project': project,
        'proposals': proposals,
    })


@login_required
def accept_proposal_view(request, proposal_id):
    """Atomic hiring transaction."""
    proposal = get_object_or_404(Proposal.objects.select_related('project', 'freelancer'), id=proposal_id)
    project = proposal.project

    if not project.is_owner(request.user) and not request.user.is_superuser:
        raise PermissionDenied("Only the project owner can accept a proposal and hire a freelancer.")

    if project.status != Project.STATUS_OPEN:
        messages.error(request, f"This project is currently '{project.get_status_display()}' and cannot hire additional talent.")
        return redirect('proposals:project_proposals', slug=project.slug)

    if request.method == 'POST':
        with transaction.atomic():
            # Lock project and proposal state
            p = Project.objects.select_for_update().get(id=project.id)
            if p.status != Project.STATUS_OPEN:
                messages.error(request, "Another hiring action was already completed for this project.")
                return redirect('proposals:project_proposals', slug=project.slug)

            # Accept this proposal
            proposal.status = Proposal.STATUS_ACCEPTED
            proposal.save(update_fields=['status', 'updated_at'])

            # Reject all conflicting proposals for this project
            other_proposals = Project.objects.get(id=project.id).proposals.exclude(id=proposal.id)
            for other in other_proposals:
                if other.status == Proposal.STATUS_PENDING:
                    other.status = Proposal.STATUS_REJECTED
                    other.save(update_fields=['status', 'updated_at'])
                    # Notify rejected freelancer
                    Notification.objects.create(
                        recipient=other.freelancer,
                        title="Proposal Status Update",
                        message=f"The client has selected another freelancer for '{project.title}'. Thank you for your submission.",
                        url=f"/projects/{project.slug}/",
                        category='proposal'
                    )

            # Update project status to In Progress
            p.status = Project.STATUS_IN_PROGRESS
            p.hired_freelancer = proposal.freelancer
            p.agreed_budget = proposal.proposed_budget
            p.save(update_fields=['status', 'hired_freelancer', 'agreed_budget', 'updated_at'])

            # Notify hired freelancer
            Notification.objects.create(
                recipient=proposal.freelancer,
                title="Congratulations! You Have Been Hired",
                message=f"Your proposal for '{project.title}' (${proposal.proposed_budget}) was accepted! Your project workspace is now active.",
                url=f"/workspace/{project.slug}/",
                category='hire'
            )

            messages.success(request, f"Successfully hired {proposal.freelancer.get_display_name()}! Welcome to your project workspace.")
            return redirect('workspace:room', slug=project.slug)

    return render(request, 'proposals/confirm_hire.html', {
        'proposal': proposal,
        'project': project,
    })


@login_required
def reject_proposal_view(request, proposal_id):
    proposal = get_object_or_404(Proposal.objects.select_related('project', 'freelancer'), id=proposal_id)
    project = proposal.project

    if not project.is_owner(request.user) and not request.user.is_superuser:
        raise PermissionDenied("Only the project owner can decline proposals.")

    if request.method == 'POST':
        proposal.status = Proposal.STATUS_REJECTED
        proposal.save(update_fields=['status', 'updated_at'])

        Notification.objects.create(
            recipient=proposal.freelancer,
            title="Proposal Status Update",
            message=f"Your proposal for '{project.title}' was reviewed and not selected at this time.",
            url=f"/projects/{project.slug}/",
            category='proposal'
        )

        messages.info(request, f"Declined proposal from {proposal.freelancer.get_display_name()}.")

    return redirect('proposals:project_proposals', slug=project.slug)
