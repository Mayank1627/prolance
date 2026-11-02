from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import FreelancerProfile, ClientProfile
from projects.models import Skill

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-neo',
            'placeholder': 'e.g. Alex Morgan',
            'autocomplete': 'name',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input-neo',
            'placeholder': 'alex@example.com',
            'autocomplete': 'email',
        })
    )
    role = forms.ChoiceField(
        choices=[
            (User.ROLE_CLIENT, 'Client — I want to hire professionals for projects'),
            (User.ROLE_FREELANCER, 'Freelancer — I want to find projects and offer services'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'sr-only peer',
        }),
        initial=User.ROLE_FREELANCER
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-neo',
            'placeholder': 'Minimum 8 characters',
            'autocomplete': 'new-password',
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-neo',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'role', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-neo',
                'placeholder': 'Unique username (e.g. alexmorgan)',
                'autocomplete': 'username',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter carefully.")

        if password and len(password) < 8:
            self.add_error('password', "Password must contain at least 8 characters.")

        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input-neo',
            'placeholder': 'Username or Email',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-neo',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )


class FreelancerProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'rounded border-2 border-neo-black text-neo-black focus:ring-0',
        })
    )

    class Meta:
        model = FreelancerProfile
        fields = [
            'headline',
            'bio',
            'hourly_rate',
            'experience_years',
            'portfolio_url',
            'github_url',
            'linkedin_url',
            'avatar',
            'is_available',
        ]
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'input-neo', 'placeholder': 'e.g. Senior Frontend Architect & UI Designer'}),
            'bio': forms.Textarea(attrs={'class': 'input-neo', 'rows': 4, 'placeholder': 'Highlight your technical background, delivered projects, and design methodology.'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'input-neo', 'placeholder': 'Hourly rate ($USD)'}),
            'experience_years': forms.NumberInput(attrs={'class': 'input-neo', 'placeholder': 'Years of professional experience'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'input-neo', 'placeholder': 'https://yourportfolio.design'}),
            'github_url': forms.URLInput(attrs={'class': 'input-neo', 'placeholder': 'https://github.com/yourhandle'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'input-neo', 'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'avatar': forms.FileInput(attrs={'class': 'input-neo'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded border-2 border-neo-black text-neo-black'}),
        }


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            'company_name',
            'company_website',
            'industry',
            'location',
            'bio',
            'avatar',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'input-neo', 'placeholder': 'Acme Labs or Studio 99'}),
            'company_website': forms.URLInput(attrs={'class': 'input-neo', 'placeholder': 'https://company.com'}),
            'industry': forms.TextInput(attrs={'class': 'input-neo', 'placeholder': 'e.g. FinTech, SaaS, Healthcare'}),
            'location': forms.TextInput(attrs={'class': 'input-neo', 'placeholder': 'e.g. San Francisco, CA or Remote'}),
            'bio': forms.Textarea(attrs={'class': 'input-neo', 'rows': 4, 'placeholder': 'Company mission and typical project needs.'}),
            'avatar': forms.FileInput(attrs={'class': 'input-neo'}),
        }
