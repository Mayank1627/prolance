from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from projects.models import Project

class Proposal(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_WITHDRAWN = 'withdrawn'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Under Review'),
        (STATUS_ACCEPTED, 'Accepted (Hired)'),
        (STATUS_REJECTED, 'Not Selected'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proposals'
    )
    cover_letter = models.TextField(help_text="Explain your approach, experience, and why you are the best fit.")
    proposed_budget = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.PositiveIntegerField(help_text="Estimated days to deliver")
    portfolio_link = models.URLField(blank=True, help_text="Direct link to relevant case study or portfolio demo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'freelancer')
        ordering = ['-created_at']

    def clean(self):
        if hasattr(self, 'project') and hasattr(self, 'freelancer'):
            if self.project.client == self.freelancer:
                raise ValidationError("Clients cannot submit proposals to their own projects.")
            if not self.pk and self.project.status != Project.STATUS_OPEN:
                raise ValidationError("Proposals can only be submitted to projects open for proposals.")

    def __str__(self):
        return f"Proposal by {self.freelancer.get_display_name()} for {self.project.title}"
