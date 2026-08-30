"""
Phase 2 Comprehensive Test Suite — Damak Municipality IMS
Tests for authentication, custom user model, user roles, and access control.

Coverage (All 17 Required Verification Tests):
    1.  User can be created.
    2.  Password is hashed.
    3.  Superuser can be created.
    4.  Valid supervisor login works.
    5.  Valid intern login works.
    6.  Invalid login fails.
    7.  Inactive user cannot log in.
    8.  Unauthenticated user cannot access supervisor dashboard.
    9.  Unauthenticated user cannot access intern dashboard.
    10. Supervisor can access supervisor dashboard.
    11. Intern can access intern dashboard.
    12. Intern cannot access supervisor dashboard.
    13. Supervisor cannot access intern dashboard.
    14. Logout works.
    15. Password change works.
    16. Generic dashboard redirects supervisor correctly.
    17. Generic dashboard redirects intern correctly.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

# ── Demo test credentials ────────────────────────────────────────────────────
SUPERVISOR_EMAIL = 'supervisor_test@example.com'
INTERN_EMAIL = 'intern_test@example.com'
INACTIVE_EMAIL = 'inactive_test@example.com'
TEST_PASSWORD = 'TestPass@9876'
NEW_PASSWORD = 'NewTestPass@1234'


class UserCreationTests(TestCase):
    """Tests 1–3: Custom User model creation, hashing, and superuser."""

    def test_01_create_regular_user(self):
        """1. User can be created."""
        user = User.objects.create_user(
            email=SUPERVISOR_EMAIL,
            password=TEST_PASSWORD,
            first_name='Test',
            last_name='Supervisor',
            role='SUPERVISOR',
        )
        self.assertEqual(user.email, SUPERVISOR_EMAIL)
        self.assertEqual(user.role, 'SUPERVISOR')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_02_password_is_hashed(self):
        """2. Password is hashed."""
        user = User.objects.create_user(
            email='hashtest@example.com',
            password=TEST_PASSWORD,
        )
        self.assertNotEqual(user.password, TEST_PASSWORD)
        self.assertTrue(user.check_password(TEST_PASSWORD))

    def test_03_create_superuser(self):
        """3. Superuser can be created."""
        superuser = User.objects.create_superuser(
            email='admin_test@example.com',
            password=TEST_PASSWORD,
            first_name='Admin',
            last_name='User',
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.role, 'SUPERVISOR')


class AuthenticationTests(TestCase):
    """Tests 4–7: Login functionality and credential validation."""

    def setUp(self):
        self.client = Client()
        self.supervisor = User.objects.create_user(
            email=SUPERVISOR_EMAIL,
            password=TEST_PASSWORD,
            first_name='Ramesh',
            last_name='Adhikari',
            role='SUPERVISOR',
        )
        self.intern = User.objects.create_user(
            email=INTERN_EMAIL,
            password=TEST_PASSWORD,
            first_name='Aayush',
            last_name='Sharma',
            role='INTERN',
        )
        self.inactive_user = User.objects.create_user(
            email=INACTIVE_EMAIL,
            password=TEST_PASSWORD,
            first_name='Inactive',
            last_name='User',
            role='INTERN',
            is_active=False,
        )
        self.login_url = reverse('login')

    def test_04_valid_supervisor_login(self):
        """4. Valid supervisor login works."""
        response = self.client.post(self.login_url, {
            'email': SUPERVISOR_EMAIL,
            'password': TEST_PASSWORD,
        })
        self.assertEqual(response.status_code, 302)
        response_dash = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response_dash.status_code, 200)
        self.assertContains(response_dash, 'Supervisor Dashboard')

    def test_05_valid_intern_login(self):
        """5. Valid intern login works."""
        response = self.client.post(self.login_url, {
            'email': INTERN_EMAIL,
            'password': TEST_PASSWORD,
        })
        self.assertEqual(response.status_code, 302)
        response_dash = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response_dash.status_code, 200)
        self.assertContains(response_dash, 'Intern Dashboard')

    def test_06_invalid_login_fails(self):
        """6. Invalid login fails."""
        response = self.client.post(self.login_url, {
            'email': SUPERVISOR_EMAIL,
            'password': 'wrongpassword999',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_07_inactive_user_cannot_login(self):
        """7. Inactive user cannot log in."""
        response = self.client.post(self.login_url, {
            'email': INACTIVE_EMAIL,
            'password': TEST_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class RoleAccessControlTests(TestCase):
    """Tests 8–13 & 16–17: Access control, dashboards, and role separation."""

    def setUp(self):
        self.client = Client()
        self.supervisor = User.objects.create_user(
            email=SUPERVISOR_EMAIL,
            password=TEST_PASSWORD,
            first_name='Ramesh',
            last_name='Adhikari',
            role='SUPERVISOR',
        )
        self.intern = User.objects.create_user(
            email=INTERN_EMAIL,
            password=TEST_PASSWORD,
            first_name='Aayush',
            last_name='Sharma',
            role='INTERN',
        )

    def test_08_unauthenticated_user_cannot_access_supervisor_dashboard(self):
        """8. Unauthenticated user cannot access supervisor dashboard."""
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_09_unauthenticated_user_cannot_access_intern_dashboard(self):
        """9. Unauthenticated user cannot access intern dashboard."""
        response = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_10_supervisor_can_access_supervisor_dashboard(self):
        """10. Supervisor can access supervisor dashboard."""
        self.client.login(username=SUPERVISOR_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Supervisor Dashboard')

    def test_11_intern_can_access_intern_dashboard(self):
        """11. Intern can access intern dashboard."""
        self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Intern Dashboard')

    def test_12_intern_cannot_access_supervisor_dashboard(self):
        """12. Intern cannot access supervisor dashboard (HTTP 403)."""
        self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'Access Denied', status_code=403)

    def test_13_supervisor_cannot_access_intern_dashboard(self):
        """13. Supervisor cannot access intern dashboard (HTTP 403)."""
        self.client.login(username=SUPERVISOR_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'Access Denied', status_code=403)

    def test_16_generic_dashboard_redirects_supervisor_correctly(self):
        """16. Generic dashboard redirects supervisor correctly."""
        self.client.login(username=SUPERVISOR_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('dashboard_redirect'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('supervisor_dashboard'))

    def test_17_generic_dashboard_redirects_intern_correctly(self):
        """17. Generic dashboard redirects intern correctly."""
        self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('dashboard_redirect'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('intern_dashboard'))


class LogoutAndPasswordTests(TestCase):
    """Tests 14–15: Logout and password change."""

    def setUp(self):
        self.client = Client()
        self.intern = User.objects.create_user(
            email=INTERN_EMAIL,
            password=TEST_PASSWORD,
            first_name='Aayush',
            last_name='Sharma',
            role='INTERN',
        )

    def test_14_logout_works(self):
        """14. Logout works."""
        self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response.status_code, 200)

        response_logout = self.client.get(reverse('logout'))
        self.assertEqual(response_logout.status_code, 302)
        self.assertEqual(response_logout.url, reverse('login'))

        # Protected dashboard blocked after logout
        response_after = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response_after.status_code, 302)

    def test_15_password_change_works(self):
        """15. Password change works."""
        self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)

        response = self.client.post(reverse('password_change'), {
            'old_password': TEST_PASSWORD,
            'new_password1': NEW_PASSWORD,
            'new_password2': NEW_PASSWORD,
        })
        self.assertEqual(response.status_code, 302)

        # Old password no longer authenticates
        self.client.logout()
        old_login = self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)
        self.assertFalse(old_login)

        # New password authenticates
        new_login = self.client.login(username=INTERN_EMAIL, password=NEW_PASSWORD)
        self.assertTrue(new_login)
