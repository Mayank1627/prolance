from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User, FreelancerProfile
from projects.models import Project, Category
from reviews.models import Review

class ReviewsAndRatingsTests(TestCase):
    def setUp(self):
        self.client_app = Client()
        self.category = Category.objects.create(name='UI/UX Design', slug='ui-design')

        self.client_user = User.objects.create_user(
            username='client_mark',
            email='mark@example.com',
            password='Password123',
            role=User.ROLE_CLIENT
        )
        self.freelancer = User.objects.create_user(
            username='freelancer_clara',
            email='clara@example.com',
            password='Password123',
            role=User.ROLE_FREELANCER
        )
        FreelancerProfile.objects.create(user=self.freelancer, headline="UI Designer")

        self.outsider = User.objects.create_user(
            username='outsider_tim',
            email='tim@example.com',
            password='Password123',
            role=User.ROLE_FREELANCER
        )

        self.project = Project.objects.create(
            client=self.client_user,
            hired_freelancer=self.freelancer,
            title='Mobile App Design System',
            category=self.category,
            budget_min=Decimal('1500.00'),
            budget_max=Decimal('2500.00'),
            agreed_budget=Decimal('2000.00'),
            deadline=timezone.now().date() + timedelta(days=5),
            description='Design system tokens and components.',
            status=Project.STATUS_IN_PROGRESS
        )

    def test_review_rejected_before_project_completion(self):
        self.client_app.login(username='client_mark', password='Password123')
        payload = {
            'rating': 5,
            'feedback': 'Great design work delivered on time.',
        }
        response = self.client_app.post(
            reverse('reviews:create_review', kwargs={'slug': self.project.slug}),
            payload,
            follow=True
        )
        self.assertContains(response, "Reviews can only be submitted after the project has been officially completed")
        self.assertFalse(Review.objects.filter(project=self.project).exists())

    def test_eligible_participants_can_submit_reviews_after_completion(self):
        self.project.status = Project.STATUS_COMPLETED
        self.project.save()

        # Client reviews freelancer
        self.client_app.login(username='client_mark', password='Password123')
        payload = {
            'rating': 5,
            'feedback': 'Exceptional delivery quality and super communication throughout.',
        }
        response = self.client_app.post(
            reverse('reviews:create_review', kwargs={'slug': self.project.slug}),
            payload,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Review.objects.filter(project=self.project, reviewer=self.client_user, reviewee=self.freelancer).exists())
        
        # Freelancer average rating matches
        self.assertEqual(self.freelancer.freelancer_profile.average_rating(), 5.0)

    def test_duplicate_review_rejected(self):
        self.project.status = Project.STATUS_COMPLETED
        self.project.save()

        Review.objects.create(
            project=self.project,
            reviewer=self.client_user,
            reviewee=self.freelancer,
            rating=5,
            feedback='Initial review.'
        )

        self.client_app.login(username='client_mark', password='Password123')
        payload = {
            'rating': 4,
            'feedback': 'Trying to leave a second review.',
        }
        response = self.client_app.post(
            reverse('reviews:create_review', kwargs={'slug': self.project.slug}),
            payload,
            follow=True
        )
        self.assertContains(response, "You have already submitted your review for this project")
        self.assertEqual(Review.objects.filter(project=self.project, reviewer=self.client_user).count(), 1)

    def test_outsider_cannot_review_project(self):
        self.project.status = Project.STATUS_COMPLETED
        self.project.save()

        self.client_app.login(username='outsider_tim', password='Password123')
        payload = {
            'rating': 1,
            'feedback': 'Malicious review from outsider.',
        }
        response = self.client_app.post(
            reverse('reviews:create_review', kwargs={'slug': self.project.slug}),
            payload
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Review.objects.filter(reviewer=self.outsider).exists())
