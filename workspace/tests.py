from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from projects.models import Project, Category
from workspace.models import ProjectDeliverable, ProjectMessage

class WorkspaceAndMessagingTests(TestCase):
    def setUp(self):
        self.client_app = Client()
        self.category = Category.objects.create(name='DevOps & Cloud', slug='devops')

        self.client_user = User.objects.create_user(
            username='client_sarah',
            email='sarah@example.com',
            password='Password123',
            role=User.ROLE_CLIENT
        )
        self.freelancer_hired = User.objects.create_user(
            username='freelancer_alex',
            email='alex@example.com',
            password='Password123',
            role=User.ROLE_FREELANCER
        )
        self.unrelated_user = User.objects.create_user(
            username='unrelated_outsider',
            email='outsider@example.com',
            password='Password123',
            role=User.ROLE_FREELANCER
        )

        self.project = Project.objects.create(
            client=self.client_user,
            hired_freelancer=self.freelancer_hired,
            title='Kubernetes Cluster Deployment',
            category=self.category,
            budget_min=Decimal('2000.00'),
            budget_max=Decimal('3000.00'),
            agreed_budget=Decimal('2500.00'),
            deadline=timezone.now().date() + timedelta(days=10),
            description='Setting up K8s cluster with persistent volumes.',
            status=Project.STATUS_IN_PROGRESS
        )

    def test_authorized_client_can_access_workspace(self):
        self.client_app.login(username='client_sarah', password='Password123')
        response = self.client_app.get(reverse('workspace:room', kwargs={'slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kubernetes Cluster Deployment')

    def test_authorized_hired_freelancer_can_access_workspace(self):
        self.client_app.login(username='freelancer_alex', password='Password123')
        response = self.client_app.get(reverse('workspace:room', kwargs={'slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_unrelated_user_denied_access(self):
        self.client_app.login(username='unrelated_outsider', password='Password123')
        response = self.client_app.get(reverse('workspace:room', kwargs={'slug': self.project.slug}))
        self.assertEqual(response.status_code, 403)

    def test_authorized_participant_can_send_message(self):
        self.client_app.login(username='freelancer_alex', password='Password123')
        msg_payload = {'message': 'Hello Sarah, I have initiated the Terraform scripts.'}
        response = self.client_app.post(
            reverse('workspace:send_message', kwargs={'slug': self.project.slug}),
            msg_payload,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ProjectMessage.objects.filter(project=self.project, sender=self.freelancer_hired).exists())

    def test_unauthorized_user_cannot_send_message(self):
        self.client_app.login(username='unrelated_outsider', password='Password123')
        msg_payload = {'message': 'Spying on the conversation.'}
        response = self.client_app.post(
            reverse('workspace:send_message', kwargs={'slug': self.project.slug}),
            msg_payload
        )
        self.assertEqual(response.status_code, 403)

    def test_freelancer_submits_deliverable_updates_status_to_review(self):
        self.client_app.login(username='freelancer_alex', password='Password123')
        payload = {
            'title': 'Production Terraform Manifests',
            'notes': 'All Kubernetes configurations tested in staging cluster.',
            'demo_url': 'https://github.com/alex/k8s-infra',
        }
        response = self.client_app.post(
            reverse('workspace:submit_deliverable', kwargs={'slug': self.project.slug}),
            payload,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ProjectDeliverable.objects.filter(project=self.project, title='Production Terraform Manifests').exists())
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_REVIEW)

    def test_client_marks_project_completed(self):
        self.client_app.login(username='client_sarah', password='Password123')
        response = self.client_app.post(
            reverse('workspace:complete_project', kwargs={'slug': self.project.slug}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_COMPLETED)
