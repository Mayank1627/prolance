from django import forms
from .models import Review, Report

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.Select(attrs={'class': 'input-neo'}, choices=[
                (5, '★★★★★ (5/5) Exceptional Quality & Communication'),
                (4, '★★★★☆ (4/5) Very Good Delivery'),
                (3, '★★★☆☆ (3/5) Satisfactory / Average'),
                (2, '★★☆☆☆ (2/5) Disappointing / Needs Improvement'),
                (1, '★☆☆☆☆ (1/5) Poor Experience'),
            ]),
            'feedback': forms.Textarea(attrs={
                'class': 'input-neo',
                'rows': 5,
                'placeholder': 'Share your honest feedback on technical quality, communication timeliness, and overall cooperation...',
            }),
        }

    def clean_feedback(self):
        fb = self.cleaned_data.get('feedback', '').strip()
        if len(fb) < 15:
            raise forms.ValidationError("Please provide at least 15 characters of constructive feedback.")
        return fb


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'input-neo'}, choices=[
                ('Misleading Specifications', 'Misleading Specifications or Fake Scope'),
                ('Inappropriate Communication', 'Inappropriate or Abusive Communication'),
                ('Payment or Escrow Dispute', 'Payment or Budget Dispute'),
                ('Intellectual Property Violation', 'Intellectual Property Violation / Stolen Work'),
                ('Spam or Scam', 'Spam, Phishing, or Scam Attempt'),
                ('Other', 'Other Violation of Community Guidelines'),
            ]),
            'details': forms.Textarea(attrs={
                'class': 'input-neo',
                'rows': 4,
                'placeholder': 'Provide clear context and links for the moderation team to inspect...',
            }),
        }
