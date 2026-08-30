"""
Phase 3 Comprehensive Test Suite — Damak Municipality IMS
Tests for Departments, Profiles, Internships, Working Days, and Access Control.

Coverage (All 17 Required Verification Tests):
    1. Department creation
    2. Duplicate department prevention
    3. Supervisor profile creation
    4. Intern profile creation
    5. Unique intern ID
    6. Unique employee ID
    7. Internship creation
    8. Invalid internship dates rejected
    9. Working-day calculation
    10. Progress calculation
    11. Remaining-day calculation
    12. Supervisor sees only assigned interns
    13. Intern sees only their own internship
    14. Intern cannot modify protected internship fields
    15. Unauthorized users cannot access protected pages
    16. Search works
    17. Status filtering works
"""

from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from interns.models import Department, SupervisorProfile, InternProfile, Internship, InternshipStatus
from interns.utils import get_working_days_count, calculate_internship_progress

User = get_user_model()


class DepartmentTests(TestCase):
    """Tests 1–2: Department creation & uniqueness."""

    def test_01_department_creation(self):
        """1. Department creation."""
        dept = Department.objects.create(name="IT Department", description="Information Technology")
        self.assertEqual(dept.name, "IT Department")
        self.assertTrue(Department.objects.filter(id=dept.id).exists())

    def test_02_duplicate_department_prevention(self):
        """2. Duplicate department prevention."""
        Department.objects.create(name="Finance")
        with self.assertRaises(IntegrityError):
            Department.objects.create(name="Finance")


class ProfileAndInternshipModelTests(TestCase):
    """Tests 3–8: Profiles, unique IDs, and Internship validation."""

    def setUp(self):
        self.dept = Department.objects.create(name="Engineering")

        self.sup_user = User.objects.create_user(
            email="sup1@example.com", password="Pass@1234", first_name="Ramesh", last_name="Adhikari", role="SUPERVISOR"
        )
        self.sup_user2 = User.objects.create_user(
            email="sup2@example.com", password="Pass@1234", first_name="Sita", last_name="Rai", role="SUPERVISOR"
        )

        self.int_user = User.objects.create_user(
            email="int1@example.com", password="Pass@1234", first_name="Aayush", last_name="Sharma", role="INTERN"
        )
        self.int_user2 = User.objects.create_user(
            email="int2@example.com", password="Pass@1234", first_name="Hari", last_name="Thapa", role="INTERN"
        )

    def test_03_supervisor_profile_creation(self):
        """3. Supervisor profile creation."""
        sup_profile = SupervisorProfile.objects.create(
            user=self.sup_user, employee_id="EMP-001", department=self.dept, position="Lead Engineer"
        )
        self.assertEqual(sup_profile.employee_id, "EMP-001")
        self.assertEqual(sup_profile.department, self.dept)

    def test_04_intern_profile_creation(self):
        """4. Intern profile creation."""
        int_profile = InternProfile.objects.create(
            user=self.int_user, intern_id="DMK-INT-001", college="TU", program="BIT"
        )
        self.assertEqual(int_profile.intern_id, "DMK-INT-001")

    def test_05_unique_intern_id(self):
        """5. Unique intern ID."""
        InternProfile.objects.create(user=self.int_user, intern_id="DMK-INT-001")
        with self.assertRaises(IntegrityError):
            InternProfile.objects.create(user=self.int_user2, intern_id="DMK-INT-001")

    def test_06_unique_employee_id(self):
        """6. Unique employee ID."""
        SupervisorProfile.objects.create(user=self.sup_user, employee_id="EMP-001")
        with self.assertRaises(IntegrityError):
            SupervisorProfile.objects.create(user=self.sup_user2, employee_id="EMP-001")

    def test_07_internship_creation(self):
        """7. Internship creation."""
        sup = SupervisorProfile.objects.create(user=self.sup_user, employee_id="EMP-001")
        intern = InternProfile.objects.create(user=self.int_user, intern_id="DMK-INT-001")
        internship = Internship.objects.create(
            intern=intern,
            supervisor=sup,
            department=self.dept,
            position="Intern",
            start_date=date(2026, 8, 1),
            expected_end_date=date(2026, 8, 31),
            status=InternshipStatus.ACTIVE
        )
        self.assertEqual(internship.status, InternshipStatus.ACTIVE)

    def test_08_invalid_internship_dates_rejected(self):
        """8. Invalid internship dates rejected."""
        sup = SupervisorProfile.objects.create(user=self.sup_user, employee_id="EMP-001")
        intern = InternProfile.objects.create(user=self.int_user, intern_id="DMK-INT-001")
        with self.assertRaises(ValidationError):
            Internship.objects.create(
                intern=intern,
                supervisor=sup,
                department=self.dept,
                position="Intern",
                start_date=date(2026, 8, 31),
                expected_end_date=date(2026, 8, 1),
            )


class WorkingDayUtilityTests(TestCase):
    """Tests 9–11: Working-day calculation logic."""

    def test_09_working_day_calculation(self):
        """9. Working-day calculation excluding Sat/Sun."""
        # 2026-08-01 (Sat) to 2026-08-07 (Fri) = 5 weekdays (Mon-Fri)
        days = get_working_days_count(date(2026, 8, 1), date(2026, 8, 7))
        self.assertEqual(days, 5)

    def test_10_progress_calculation(self):
        """10. Progress calculation percentage."""
        dept = Department.objects.create(name="IT")
        sup_u = User.objects.create_user(email="s1@ex.com", password="P1", role="SUPERVISOR")
        int_u = User.objects.create_user(email="i1@ex.com", password="P1", role="INTERN")
        sup = SupervisorProfile.objects.create(user=sup_u, employee_id="E1")
        intern = InternProfile.objects.create(user=int_u, intern_id="I1")

        # Start Aug 3 (Mon), End Aug 14 (Fri) = 10 working days
        internship = Internship.objects.create(
            intern=intern, supervisor=sup, department=dept, position="Dev",
            start_date=date(2026, 8, 3), expected_end_date=date(2026, 8, 14), status="ACTIVE"
        )
        # As of Aug 7 (Fri) = 5 working days completed => 50%
        metrics = calculate_internship_progress(internship, current_date=date(2026, 8, 7))
        self.assertEqual(metrics['total_working_days'], 10)
        self.assertEqual(metrics['completed_working_days'], 5)
        self.assertEqual(metrics['progress_percentage'], 50)

    def test_11_remaining_day_calculation(self):
        """11. Remaining-day calculation."""
        dept = Department.objects.create(name="IT")
        sup_u = User.objects.create_user(email="s2@ex.com", password="P1", role="SUPERVISOR")
        int_u = User.objects.create_user(email="i2@ex.com", password="P1", role="INTERN")
        sup = SupervisorProfile.objects.create(user=sup_u, employee_id="E2")
        intern = InternProfile.objects.create(user=int_u, intern_id="I2")

        internship = Internship.objects.create(
            intern=intern, supervisor=sup, department=dept, position="Dev",
            start_date=date(2026, 8, 3), expected_end_date=date(2026, 8, 14), status="ACTIVE"
        )
        # As of Aug 7 (Fri), remaining days (Aug 8..Aug 14) = 5 working days
        metrics = calculate_internship_progress(internship, current_date=date(2026, 8, 7))
        self.assertEqual(metrics['remaining_working_days'], 5)


class AccessControlAndViewsTests(TestCase):
    """Tests 12–17: Server-side security, views, search, and filtering."""

    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="IT Department")

        # Supervisor A
        self.sup_a_user = User.objects.create_user(
            email="sup_a@example.com", password="Password@123", first_name="Supervisor", last_name="A", role="SUPERVISOR"
        )
        self.sup_a_prof = SupervisorProfile.objects.create(user=self.sup_a_user, employee_id="EMP-A", department=self.dept)

        # Supervisor B
        self.sup_b_user = User.objects.create_user(
            email="sup_b@example.com", password="Password@123", first_name="Supervisor", last_name="B", role="SUPERVISOR"
        )
        self.sup_b_prof = SupervisorProfile.objects.create(user=self.sup_b_user, employee_id="EMP-B", department=self.dept)

        # Intern A (Assigned to Supervisor A)
        self.int_a_user = User.objects.create_user(
            email="int_a@example.com", password="Password@123", first_name="Intern", last_name="Alpha", role="INTERN"
        )
        self.int_a_prof = InternProfile.objects.create(user=self.int_a_user, intern_id="DMK-INT-001")
        self.ship_a = Internship.objects.create(
            intern=self.int_a_prof, supervisor=self.sup_a_prof, department=self.dept, position="Dev Intern",
            start_date=date(2026, 8, 1), expected_end_date=date(2026, 8, 31), status="ACTIVE"
        )

        # Intern B (Assigned to Supervisor B)
        self.int_b_user = User.objects.create_user(
            email="int_b@example.com", password="Password@123", first_name="Intern", last_name="Beta", role="INTERN"
        )
        self.int_b_prof = InternProfile.objects.create(user=self.int_b_user, intern_id="DMK-INT-002")
        self.ship_b = Internship.objects.create(
            intern=self.int_b_prof, supervisor=self.sup_b_prof, department=self.dept, position="Design Intern",
            start_date=date(2026, 8, 1), expected_end_date=date(2026, 8, 31), status="COMPLETED"
        )

    def test_12_supervisor_sees_only_assigned_interns(self):
        """12. Supervisor sees only assigned interns."""
        self.client.login(username="sup_a@example.com", password="Password@123")
        response = self.client.get(reverse('supervisor_my_interns'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DMK-INT-001")
        self.assertNotContains(response, "DMK-INT-002")

    def test_13_intern_sees_only_their_own_internship(self):
        """13. Intern sees only their own internship."""
        self.client.login(username="int_a@example.com", password="Password@123")
        response = self.client.get(reverse('intern_my_internship'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DMK-INT-001")
        self.assertNotContains(response, "DMK-INT-002")

    def test_14_intern_cannot_modify_protected_internship_fields(self):
        """14. Intern cannot modify protected internship fields via profile form."""
        self.client.login(username="int_a@example.com", password="Password@123")
        response = self.client.post(reverse('intern_profile'), {
            'phone': '+977-9800000000',
            'address': 'New Address',
            # Attempt to inject protected fields
            'intern_id': 'HACKED-ID',
            'status': 'COMPLETED',
        })
        self.assertEqual(response.status_code, 302)
        self.int_a_prof.refresh_from_db()
        self.assertEqual(self.int_a_prof.intern_id, 'DMK-INT-001')
        self.assertEqual(self.int_a_prof.phone, '+977-9800000000')

    def test_15_unauthorized_users_cannot_access_protected_pages(self):
        """15. Unauthorized users cannot access protected pages."""
        # Unauthenticated access to department list -> 302 to login
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 302)

        # Intern attempting to access department list -> 302 to login or 403
        self.client.login(username="int_a@example.com", password="Password@123")
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 302)

    def test_16_search_works(self):
        """16. Search works on My Interns page."""
        self.client.login(username="sup_a@example.com", password="Password@123")
        # Search for "Alpha"
        response = self.client.get(reverse('supervisor_my_interns') + '?q=Alpha')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DMK-INT-001")

        # Search for non-existing query
        response_empty = self.client.get(reverse('supervisor_my_interns') + '?q=NonExistent')
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, "No Assigned Interns Found")

    def test_17_status_filtering_works(self):
        """17. Status filtering works on My Interns page."""
        self.client.login(username="sup_a@example.com", password="Password@123")
        # Filter for ACTIVE
        response = self.client.get(reverse('supervisor_my_interns') + '?status=ACTIVE')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DMK-INT-001")

        # Filter for COMPLETED (Supervisor A has no completed interns)
        response_completed = self.client.get(reverse('supervisor_my_interns') + '?status=COMPLETED')
        self.assertEqual(response_completed.status_code, 200)
        self.assertContains(response_completed, "No Assigned Interns Found")
