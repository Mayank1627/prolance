from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from projects.models import Project, Category, Skill, SavedProject
from proposals.models import Proposal

class ProjectManagementTests(TestCase):
    def setUp(self):
        self.client_app = Client()
        self.category = Category.objects.create(name='UI/UX Design', slug='ui-ux-design')
        self.skill = Skill.objects.create(name='Figma', slug='figma', category=self.category)

        # Clients
        self.client_user_1 = User.objects.create_user(
            username='client_one',
            email='client1@example.com',
            password='Password123',
            role=User.ROLE_CLIENT
        )
        self.client_user_2 = User.objects.create_user(
            username='client_two',
            email='client2@example.com',
            password='Password123',
            role=User.ROLE_CLIENT
        )

        # Freelancer
        self.freelancer = User.objects.create_user(
            username='freelancer_bob',
            email='bob@example.com',
            password='Password123',
            role=User.ROLE_FREELANCER
        )

    def test_client_can_create_project(self):
        self.client_app.login(username='client_one', password='Password123')
        payload = {
            'title': 'New E-commerce Dashboard',
            'category': self.category.id,
            'project_type': Project.TYPE_FIXED,
            'budget_min': '500.00',
            'budget_max': '1500.00',
            'deadline': (timezone.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'required_skills': [self.skill.id],
            'description': 'Building a high-converting neo-brutalist storefront dashboard with responsive layouts.',
        }
        response = self.client_app.post(reverse('projects:create'), payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Project.objects.filter(title='New E-commerce Dashboard').exists())
        proj = Project.objects.get(title='New E-commerce Dashboard')
        self.assertEqual(proj.client, self.client_user_1)
        self.assertEqual(proj.status, Project.STATUS_OPEN)

    def test_freelancer_cannot_create_project(self):
        self.client_app.login(username='freelancer_bob', password='Password123')
        response = self.client_app.get(reverse('projects:create'))
        self.assertEqual(response.status_code, 302)  # redirected away

    def test_client_can_edit_own_project(self):
        self.client_app.login(username='client_one', password='Password123')
        project = Project.objects.create(
            client=self.client_user_1,
            title='Initial Project Spec',
            category=self.category,
            budget_min=Decimal('500.00'),
            budget_max=Decimal('1000.00'),
            deadline=timezone.now().date() + timedelta(days=7),
            description='Original description of project milestones.'
        )
        edit_payload = {
            'title': 'Updated Project Spec V2',
            'category': self.category.id,
            'project_type': Project.TYPE_FIXED,
            'budget_min': '600.00',
            'budget_max': '1200.00',
            'deadline': (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'description': 'Updated description with extra milestone deliverables.',
        }
        response = self.client_app.post(reverse('projects:edit', kwargs={'slug': project.slug}), edit_payload, follow=True)
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.title, 'Updated Project Spec V2')

    def test_client_cannot_edit_another_clients_project(self):
        # Project owned by client_one
        project = Project.objects.create(
            client=self.client_user_1,
            title='Client One Private Project',
            category=self.category,
            budget_min=Decimal('1000.00'),
            budget_max=Decimal('2000.00'),
            deadline=timezone.now().date() + timedelta(days=7),
            description='Confidential enterprise specs.'
        )
        # Login as client_two
        self.client_app.login(username='client_two', password='Password123')
        response = self.client_app.get(reverse('projects:edit', kwargs={'slug': project.slug}))
        self.assertEqual(response.status_code, 403)

    def test_invalid_project_data_rejected(self):
        self.client_app.login(username='client_one', password='Password123')
        # max budget < min budget, deadline in past
        payload = {
            'title': 'Bad Project',
            'category': self.category.id,
            'project_type': Project.TYPE_FIXED,
            'budget_min': '1000.00',
            'budget_max': '500.00',  # invalid
            'deadline': (timezone.now() - timedelta(days=5)).strftime('%Y-%m-%d'),  # past
            'description': 'Invalid specs.',
        }
        response = self.client_app.post(reverse('projects:create'), payload)
        self.assertContains(response, "Maximum budget must be greater than or equal to minimum budget")
        self.assertContains(response, "cannot be scheduled in the past")
        self.assertFalse(Project.objects.filter(title='Bad Project').exists())

    def test_project_filtering_and_search(self):
        Project.objects.create(
            client=self.client_user_1,
            title='Mobile App for Logistics',
            category=self.category,
            budget_min=Decimal('1000.00'),
            budget_max=Decimal('2000.00'),
            deadline=timezone.now().date() + timedelta(days=7),
            description='Tracking drivers and packages.',
            status=Project.STATUS_OPEN
        )
        Project.objects.create(
            client=self.client_user_1,
            title='Cloud Infrastructure Terraform',
            category=self.category,
            budget_min=Decimal('3000.00'),
            budget_max=Decimal('5000.00'),
            deadline=timezone.now().date() + timedelta(days=7),
            description='Automating AWS deployments.',
            status=Project.STATUS_OPEN
        )
        # Search query
        response = self.client_app.get(reverse('projects:browse') + '?q=Logistics')
        self.assertContains(response, 'Mobile App for Logistics')
        self.assertNotContains(response, 'Cloud Infrastructure Terraform')

    def test_freelancer_bookmark_saved_project(self):
        self.client_app.login(username='freelancer_bob', password='Password123')
        project = Project.objects.create(
            client=self.client_user_1,
            title='Bookmarkable Task',
            category=self.category,
            budget_min=Decimal('500.00'),
            budget_max=Decimal('1000.00'),
            deadline=timezone.now().date() + timedelta(days=7),
            description='Bookmark test description.'
        )
        # Toggle save
        response = self.client_app.post(reverse('projects:toggle_save', kwargs={'project_id': project.id}))
        self.assertTrue(SavedProject.objects.filter(user=self.freelancer, project=project).exists())

        # Toggle again removes it
        response2 = self.client_app.post(reverse('projects:toggle_save', kwargs={'project_id': project.id}))
        self.assertFalse(SavedProject.objects.filter(user=self.freelancer, project=project).exists())
