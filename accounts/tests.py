from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, FreelancerProfile, ClientProfile

class AccountsAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')

    def test_successful_freelancer_registration(self):
        payload = {
            'username': 'john_freelance',
            'full_name': 'John Freelancer',
            'email': 'john@example.com',
            'role': User.ROLE_FREELANCER,
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
        }
        response = self.client.post(self.register_url, payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='john_freelance').exists())
        user = User.objects.get(username='john_freelance')
        self.assertEqual(user.role, User.ROLE_FREELANCER)
        self.assertTrue(hasattr(user, 'freelancer_profile'))

    def test_successful_client_registration(self):
        payload = {
            'username': 'jane_client',
            'full_name': 'Jane Client',
            'email': 'jane@example.com',
            'role': User.ROLE_CLIENT,
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
        }
        response = self.client.post(self.register_url, payload, follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='jane_client')
        self.assertEqual(user.role, User.ROLE_CLIENT)
        self.assertTrue(hasattr(user, 'client_profile'))

    def test_duplicate_email_registration_rejected(self):
        User.objects.create_user(
            username='existing_user',
            email='duplicate@example.com',
            password='Password123'
        )
        payload = {
            'username': 'new_user',
            'full_name': 'New User',
            'email': 'duplicate@example.com',
            'role': User.ROLE_FREELANCER,
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='new_user').exists())
        self.assertContains(response, "An account with this email address already exists.")

    def test_password_mismatch_validation(self):
        payload = {
            'username': 'mismatch_user',
            'full_name': 'Mismatch Test',
            'email': 'mismatch@example.com',
            'role': User.ROLE_FREELANCER,
            'password': 'SecurePassword123!',
            'confirm_password': 'DifferentPassword456!',
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatch_user').exists())
        self.assertContains(response, "Passwords do not match")

    def test_password_min_length_validation(self):
        payload = {
            'username': 'short_pass_user',
            'full_name': 'Short Pass',
            'email': 'short@example.com',
            'role': User.ROLE_FREELANCER,
            'password': 'short',
            'confirm_password': 'short',
        }
        response = self.client.post(self.register_url, payload)
        self.assertContains(response, "at least 8 characters")

    def test_successful_login_and_logout(self):
        user = User.objects.create_user(
            username='active_member',
            email='member@example.com',
            password='MemberPassword123'
        )
        # Login
        response = self.client.post(self.login_url, {
            'username': 'active_member',
            'password': 'MemberPassword123',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

        # Logout
        logout_response = self.client.post(self.logout_url, follow=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertFalse(logout_response.context['user'].is_authenticated)

    def test_invalid_login_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'non_existent_user',
            'password': 'WrongPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password credentials.")

    def test_protected_page_redirects_anonymous_user(self):
        response = self.client.get(reverse('accounts:edit_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)
