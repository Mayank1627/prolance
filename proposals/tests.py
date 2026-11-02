from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from projects.models import Project, Category
from proposals.models import Proposal

class ProposalsAndHiringTests(TestCase):
    def setUp(self):
        self.client_app = Client()
        self.category = Category.objects.create(name='Web Development', slug='web-dev')

        self.client_user = User.objects.create_user(
            username='client_alice',
            email='alice@example.com',
            password='Password123',
            role=User.ROLE_CLIENT
        )
        self.freelancer_1 = User.objects.create_user(
            username='freelancer_dan',
            email='dan@example.com',
            password='Password123',
            role=User.ROLE_FREELANCER
        )
        self.freelancer_2 = User.objects.create_user(
            username='freelancer_eve',
            email='eve@example.com',
            password='Password123',
            role=User.ROLE_FREELANCER
        )

        self.project = Project.objects.create(
            client=self.client_user,
            title='Real-Time Dashboard Project',
            category=self.category,
            budget_min=Decimal('1000.00'),
            budget_max=Decimal('2000.00'),
            deadline=timezone.now().date() + timedelta(days=14),
            description='Django backend with WebSocket / HTMX dashboard.',
            status=Project.STATUS_OPEN
        )

    def test_freelancer_can_submit_proposal(self):
        self.client_app.login(username='freelancer_dan', password='Password123')
        payload = {
            'proposed_budget': '1500.00',
            'estimated_days': 10,
            'portfolio_link': 'https://dan.dev',
            'cover_letter': 'I have built multiple real-time dashboards with Django and Tailwind CSS.',
        }
        response = self.client_app.post(reverse('proposals:submit', kwargs={'slug': self.project.slug}), payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Proposal.objects.filter(project=self.project, freelancer=self.freelancer_1).exists())
        prop = Proposal.objects.get(project=self.project, freelancer=self.freelancer_1)
        self.assertEqual(prop.proposed_budget, Decimal('1500.00'))
        self.assertEqual(prop.status, Proposal.STATUS_PENDING)

    def test_duplicate_proposal_prevented(self):
        Proposal.objects.create(
            project=self.project,
            freelancer=self.freelancer_1,
            proposed_budget=Decimal('1200.00'),
            estimated_days=7,
            cover_letter='First proposal.'
        )
        self.client_app.login(username='freelancer_dan', password='Password123')
        payload = {
            'proposed_budget': '1400.00',
            'estimated_days': 8,
            'cover_letter': 'Second attempt duplicate proposal.',
        }
        response = self.client_app.post(reverse('proposals:submit', kwargs={'slug': self.project.slug}), payload, follow=True)
        self.assertContains(response, "You have already submitted a proposal for this project.")
        self.assertEqual(Proposal.objects.filter(project=self.project, freelancer=self.freelancer_1).count(), 1)

    def test_client_cannot_submit_proposal_to_own_project(self):
        self.client_app.login(username='client_alice', password='Password123')
        payload = {
            'proposed_budget': '500.00',
            'estimated_days': 5,
            'cover_letter': 'Client bidding on self.',
        }
        response = self.client_app.post(reverse('proposals:submit', kwargs={'slug': self.project.slug}), payload, follow=True)
        self.assertContains(response, "Only registered Freelancers may submit project proposals")
        self.assertFalse(Proposal.objects.filter(project=self.project, freelancer=self.client_user).exists())

    def test_only_owner_can_accept_proposal(self):
        prop = Proposal.objects.create(
            project=self.project,
            freelancer=self.freelancer_1,
            proposed_budget=Decimal('1500.00'),
            estimated_days=10,
            cover_letter='Ready to commence work immediately.'
        )
        # Login as non-owner (freelancer_eve)
        self.client_app.login(username='freelancer_eve', password='Password123')
        response = self.client_app.post(reverse('proposals:accept', kwargs={'proposal_id': prop.id}))
        self.assertEqual(response.status_code, 403)

    def test_atomic_hiring_updates_project_and_rejects_competitors(self):
        prop_dan = Proposal.objects.create(
            project=self.project,
            freelancer=self.freelancer_1,
            proposed_budget=Decimal('1500.00'),
            estimated_days=10,
            cover_letter='Dan proposal for the work.'
        )
        prop_eve = Proposal.objects.create(
            project=self.project,
            freelancer=self.freelancer_2,
            proposed_budget=Decimal('1600.00'),
            estimated_days=12,
            cover_letter='Eve proposal for the work.'
        )

        # Login as client owner and accept Dan
        self.client_app.login(username='client_alice', password='Password123')
        response = self.client_app.post(reverse('proposals:accept', kwargs={'proposal_id': prop_dan.id}), follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify Dan is accepted
        prop_dan.refresh_from_db()
        self.assertEqual(prop_dan.status, Proposal.STATUS_ACCEPTED)

        # Verify Eve is rejected
        prop_eve.refresh_from_db()
        self.assertEqual(prop_eve.status, Proposal.STATUS_REJECTED)

        # Verify Project is In Progress with assigned freelancer and agreed budget
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_IN_PROGRESS)
        self.assertEqual(self.project.hired_freelancer, self.freelancer_1)
        self.assertEqual(self.project.agreed_budget, Decimal('1500.00'))

    def test_closed_project_cannot_receive_proposals(self):
        self.project.status = Project.STATUS_CLOSED
        self.project.save()

        self.client_app.login(username='freelancer_dan', password='Password123')
        payload = {
            'proposed_budget': '1500.00',
            'estimated_days': 10,
            'cover_letter': 'Trying to bid on closed project.',
        }
        response = self.client_app.post(reverse('proposals:submit', kwargs={'slug': self.project.slug}), payload, follow=True)
        self.assertContains(response, "This project is no longer accepting new proposals")
        self.assertFalse(Proposal.objects.filter(project=self.project).exists())
