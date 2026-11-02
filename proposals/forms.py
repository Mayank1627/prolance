from django import forms
from .models import Proposal

class ProposalSubmissionForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['proposed_budget', 'estimated_days', 'portfolio_link', 'cover_letter']
        widgets = {
            'proposed_budget': forms.NumberInput(attrs={
                'class': 'input-neo',
                'placeholder': 'Your proposed total price ($ USD)',
            }),
            'estimated_days': forms.NumberInput(attrs={
                'class': 'input-neo',
                'placeholder': 'e.g. 14 days',
            }),
            'portfolio_link': forms.URLInput(attrs={
                'class': 'input-neo',
                'placeholder': 'https://github.com/project-demo or live link (optional)',
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'input-neo',
                'rows': 6,
                'placeholder': 'Describe your relevant past experience, your technical approach to this challenge, and when you can start...',
            }),
        }

    def clean_proposed_budget(self):
        budget = self.cleaned_data.get('proposed_budget')
        if budget is not None and budget <= 0:
            raise forms.ValidationError("Proposed price must be greater than zero.")
        return budget

    def clean_estimated_days(self):
        days = self.cleaned_data.get('estimated_days')
        if days is not None and days <= 0:
            raise forms.ValidationError("Estimated delivery timeframe must be at least 1 day.")
        return days

    def clean_cover_letter(self):
        cover = self.cleaned_data.get('cover_letter', '').strip()
        if len(cover) < 30:
            raise forms.ValidationError("Please provide a more detailed proposal (at least 30 characters).")
        return cover
