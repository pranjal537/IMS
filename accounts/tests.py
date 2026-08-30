"""
Phase 2 Test Suite — Damak Municipality IMS
Tests for authentication, user roles, and access control.

Coverage:
    1.  User creation
    2.  Superuser creation
    3.  Password hashing (not stored in plain text)
    4.  Successful login
    5.  Invalid login
    6.  Supervisor dashboard access by supervisor
    7.  Intern dashboard access by intern
    8.  Supervisor blocked from intern-only pages (403)
    9.  Intern blocked from supervisor-only pages (403)
    10. Unauthenticated users redirected to login
    11. Logout clears session
    12. Password change
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

# ── Demo test credentials — for tests only ───────────────────────────────────
SUPERVISOR_EMAIL = 'supervisor_test@example.com'
INTERN_EMAIL = 'intern_test@example.com'
TEST_PASSWORD = 'TestPass@9876'
NEW_PASSWORD = 'NewTestPass@1234'


class UserCreationTests(TestCase):
    """Tests 1–3: Model-level user creation and security."""

    def test_01_create_regular_user(self):
        """Test 1: create_user() produces a valid active user."""
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

    def test_02_create_superuser(self):
        """Test 2: create_superuser() produces a valid admin user."""
        superuser = User.objects.create_superuser(
            email='admin_test@example.com',
            password=TEST_PASSWORD,
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_03_password_is_hashed(self):
        """Test 3: Passwords are hashed — never stored in plain text."""
        user = User.objects.create_user(
            email='hashtest@example.com',
            password=TEST_PASSWORD,
        )
        # The raw password must NOT appear in the stored hash
        self.assertNotEqual(user.password, TEST_PASSWORD)
        # Django's check_password must verify the plain password correctly
        self.assertTrue(user.check_password(TEST_PASSWORD))


class AuthenticationTests(TestCase):
    """Tests 4–5: Login flow."""

    def setUp(self):
        self.client = Client()
        self.supervisor = User.objects.create_user(
            email=SUPERVISOR_EMAIL,
            password=TEST_PASSWORD,
            first_name='Ramesh',
            last_name='Adhikari',
            role='SUPERVISOR',
        )
        self.login_url = reverse('login')

    def test_04_successful_login(self):
        """Test 4: Valid credentials authenticate the user and redirect to dashboard."""
        response = self.client.post(self.login_url, {
            'email': SUPERVISOR_EMAIL,
            'password': TEST_PASSWORD,
        })
        # Should redirect (302) to dashboard_redirect
        self.assertEqual(response.status_code, 302)
        # User should now be authenticated
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_05_invalid_login_rejected(self):
        """Test 5: Wrong password does not authenticate and shows error."""
        response = self.client.post(self.login_url, {
            'email': SUPERVISOR_EMAIL,
            'password': 'wrongpassword999',
        })
        # Should stay on login page (200 means re-rendered form)
        self.assertEqual(response.status_code, 200)
        # Error message shown but does not reveal email existence
        self.assertContains(response, 'Invalid email or password')
        # User must NOT be authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class RoleAccessControlTests(TestCase):
    """Tests 6–10: Role-based access control."""

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

    def test_06_supervisor_can_access_supervisor_dashboard(self):
        """Test 6: Supervisor can access /supervisor/dashboard/."""
        self.client.login(username=SUPERVISOR_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Supervisor Dashboard')

    def test_07_intern_can_access_intern_dashboard(self):
        """Test 7: Intern can access /intern/dashboard/."""
        self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Intern Dashboard')

    def test_08_supervisor_blocked_from_intern_dashboard(self):
        """Test 8: Supervisor receives 403 when accessing intern-only page."""
        self.client.login(username=SUPERVISOR_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_09_intern_blocked_from_supervisor_dashboard(self):
        """Test 9: Intern receives 403 when accessing supervisor-only page."""
        self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_10_unauthenticated_user_redirected_to_login(self):
        """Test 10: Unauthenticated access to protected pages redirects to login."""
        # Supervisor dashboard
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertIn(response.status_code, [302, 403])
        # Intern dashboard
        response = self.client.get(reverse('intern_dashboard'))
        self.assertIn(response.status_code, [302, 403])
        # Dashboard redirect
        response = self.client.get(reverse('dashboard_redirect'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)


class LogoutTests(TestCase):
    """Test 11: Logout behaviour."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email=SUPERVISOR_EMAIL,
            password=TEST_PASSWORD,
            role='SUPERVISOR',
        )

    def test_11_logout_clears_session(self):
        """Test 11: Logout removes session and protected pages become inaccessible."""
        # Log in first
        self.client.login(username=SUPERVISOR_EMAIL, password=TEST_PASSWORD)
        # Confirm access works
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response.status_code, 200)

        # Log out
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

        # After logout protected pages must no longer be accessible
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertIn(response.status_code, [302, 403])


class PasswordChangeTests(TestCase):
    """Test 12: Password change functionality."""

    def setUp(self):
        self.client = Client()
        self.intern = User.objects.create_user(
            email=INTERN_EMAIL,
            password=TEST_PASSWORD,
            first_name='Aayush',
            last_name='Sharma',
            role='INTERN',
        )

    def test_12_password_change(self):
        """Test 12: Intern can change password and log in with new password."""
        self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)

        # Submit password change form
        response = self.client.post(reverse('password_change'), {
            'old_password': TEST_PASSWORD,
            'new_password1': NEW_PASSWORD,
            'new_password2': NEW_PASSWORD,
        })
        # Should redirect after successful change
        self.assertEqual(response.status_code, 302)

        # Old password must no longer work
        self.client.logout()
        old_login = self.client.login(username=INTERN_EMAIL, password=TEST_PASSWORD)
        self.assertFalse(old_login)

        # New password must work
        new_login = self.client.login(username=INTERN_EMAIL, password=NEW_PASSWORD)
        self.assertTrue(new_login)
