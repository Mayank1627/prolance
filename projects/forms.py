from django import forms
from django.utils import timezone
from .models import Project, Category, Skill

class ProjectForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a Category",
        widget=forms.Select(attrs={'class': 'input-neo'})
    )
    required_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'input-neo h-32'})
    )

    class Meta:
        model = Project
        fields = [
            'title',
            'category',
            'description',
            'project_type',
            'budget_min',
            'budget_max',
            'deadline',
            'required_skills',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input-neo',
                'placeholder': 'e.g. Neo-Brutalist Design System & Next.js Implementation',
            }),
            'description': forms.Textarea(attrs={
                'class': 'input-neo',
                'rows': 6,
                'placeholder': 'Provide detailed scope of work, technical requirements, acceptance criteria, and expected deliverables...',
            }),
            'project_type': forms.Select(attrs={'class': 'input-neo'}),
            'budget_min': forms.NumberInput(attrs={'class': 'input-neo', 'placeholder': 'Minimum Budget ($)'}),
            'budget_max': forms.NumberInput(attrs={'class': 'input-neo', 'placeholder': 'Maximum Budget ($)'}),
            'deadline': forms.DateInput(attrs={'class': 'input-neo', 'type': 'date'}),
        }

    def clean_budget_min(self):
        budget_min = self.cleaned_data.get('budget_min')
        if budget_min is not None and budget_min < 5:
            raise forms.ValidationError("Minimum budget must be at least $5.")
        return budget_min

    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get('budget_min')
        budget_max = cleaned_data.get('budget_max')
        deadline = cleaned_data.get('deadline')

        if budget_min is not None and budget_max is not None:
            if budget_max < budget_min:
                self.add_error('budget_max', "Maximum budget must be greater than or equal to minimum budget.")

        if deadline and deadline < timezone.now().date():
            self.add_error('deadline', "Project deadline cannot be scheduled in the past.")

        return cleaned_data
