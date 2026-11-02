from django import forms
from .models import ProjectDeliverable, ProjectMessage

class DeliverableSubmissionForm(forms.ModelForm):
    class Meta:
        model = ProjectDeliverable
        fields = ['title', 'notes', 'demo_url', 'file_attachment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input-neo',
                'placeholder': 'e.g. Final Production Build & Documentation',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'input-neo',
                'rows': 4,
                'placeholder': 'Explain what was completed, how to test the deliverable, and release notes...',
            }),
            'demo_url': forms.URLInput(attrs={
                'class': 'input-neo',
                'placeholder': 'https://github.com/repo or https://staging.app (optional)',
            }),
            'file_attachment': forms.FileInput(attrs={'class': 'input-neo'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        demo_url = cleaned_data.get('demo_url')
        attachment = cleaned_data.get('file_attachment')
        if not demo_url and not attachment:
            raise forms.ValidationError("Please provide either a demo/repository link or upload a deliverable file.")
        return cleaned_data


class DeliverableReviewForm(forms.ModelForm):
    class Meta:
        model = ProjectDeliverable
        fields = ['status', 'client_feedback']
        widgets = {
            'status': forms.Select(attrs={'class': 'input-neo'}, choices=[
                (ProjectDeliverable.STATUS_APPROVED, 'Approve Deliverable (Satisfactory)'),
                (ProjectDeliverable.STATUS_REVISION, 'Request Revisions (Changes Needed)'),
            ]),
            'client_feedback': forms.Textarea(attrs={
                'class': 'input-neo',
                'rows': 3,
                'placeholder': 'Provide specific feedback or approval remarks for the freelancer...',
            }),
        }


class ProjectMessageForm(forms.ModelForm):
    class Meta:
        model = ProjectMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'input-neo',
                'rows': 2,
                'placeholder': 'Write project message or deliverable question...',
            }),
            'attachment': forms.FileInput(attrs={'class': 'hidden', 'id': 'chat-file-input'}),
        }

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if not msg and not self.files.get('attachment'):
            raise forms.ValidationError("Cannot send an empty message.")
        return msg
