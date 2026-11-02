from django.db import models
from django.conf import settings
from projects.models import Project

class ProjectDeliverable(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_APPROVED = 'approved'
    STATUS_REVISION = 'revision'
    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted for Client Review'),
        (STATUS_APPROVED, 'Approved by Client'),
        (STATUS_REVISION, 'Revisions Requested'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='deliverables')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deliverables_submitted')
    title = models.CharField(max_length=200, help_text="e.g. Initial UI Component Library or Final Production Build")
    notes = models.TextField(help_text="Detailed description of files delivered and instructions for testing")
    file_attachment = models.FileField(upload_to='deliverables/', blank=True, null=True)
    demo_url = models.URLField(blank=True, help_text="Live preview URL or GitHub repository / Figma link")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    client_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Deliverable: {self.title} ({self.get_status_display()})"


class ProjectMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_project_messages')
    message = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message by {self.sender.get_display_name()} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
