from django.db import models
from django.conf import settings

class Notification(models.Model):
    CATEGORY_CHOICES = [
        ('proposal', 'Proposal Update'),
        ('hire', 'Hiring Update'),
        ('message', 'New Message'),
        ('deliverable', 'Deliverable Submitted'),
        ('review', 'Review Received'),
        ('system', 'System Notice'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, help_text="Relative URL to navigate to when clicked")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='system')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient.username}: {self.title}"
