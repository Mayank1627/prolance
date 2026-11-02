import urllib.parse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg

class User(AbstractUser):
    ROLE_CLIENT = 'client'
    ROLE_FREELANCER = 'freelancer'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Client (Hire Talent)'),
        (ROLE_FREELANCER, 'Freelancer (Find Work)'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_FREELANCER)
    email = models.EmailField(unique=True, verbose_name='Email Address')
    full_name = models.CharField(max_length=150, blank=True)
    is_verified = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['email']

    def is_client_user(self):
        return self.role == self.ROLE_CLIENT or self.is_superuser

    def is_freelancer_user(self):
        return self.role == self.ROLE_FREELANCER

    def get_display_name(self):
        return self.full_name.strip() if self.full_name else self.username

    def __str__(self):
        return f"{self.get_display_name()} ({self.get_role_display()})"


class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    headline = models.CharField(max_length=200, blank=True, help_text="e.g. Senior Brand Designer & Full-Stack Architect")
    bio = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=35.00)
    experience_years = models.PositiveIntegerField(default=2)
    portfolio_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def average_rating(self):
        avg = self.user.reviews_received.aggregate(avg_score=Avg('rating'))['avg_score']
        return round(avg, 1) if avg is not None else 0.0

    def total_reviews(self):
        return self.user.reviews_received.count()

    def get_avatar_url(self):
        if self.avatar:
            try:
                return self.avatar.url
            except Exception:
                pass
        name = urllib.parse.quote(self.user.get_display_name())
        return f"https://api.dicebear.com/7.x/bottts/svg?seed={name}&backgroundColor=FFE600"

    def __str__(self):
        return f"Freelancer: {self.user.get_display_name()}"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=150, blank=True)
    company_website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_avatar_url(self):
        if self.avatar:
            try:
                return self.avatar.url
            except Exception:
                pass
        name = urllib.parse.quote(self.company_name or self.user.get_display_name())
        return f"https://api.dicebear.com/7.x/identicon/svg?seed={name}&backgroundColor=2DD4BF"

    def __str__(self):
        return f"Client: {self.company_name or self.user.get_display_name()}"
