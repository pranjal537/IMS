"""
Phase 5 Comprehensive Test Suite — Damak Municipality IMS
Tests for Daily Logbook, Form Validation, Intern/Supervisor workflows, and Access Control.
"""

from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from interns.models import Department, SupervisorProfile, InternProfile, Internship, InternshipStatus
from attendance.models import Attendance, AttendanceStatus
from logbook.models import DailyLog, DailyLogStatus

User = get_user_model()


class DailyLogbookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="IT")

        # Supervisor 1
        self.sup1_user = User.objects.create_user(email="s1@example.com", password="Password@123", role="SUPERVISOR")
        self.sup1 = SupervisorProfile.objects.create(user=self.sup1_user, employee_id="E-1", department=self.dept)

        # Supervisor 2
        self.sup2_user = User.objects.create_user(email="s2@example.com", password="Password@123", role="SUPERVISOR")
        self.sup2 = SupervisorProfile.objects.create(user=self.sup2_user, employee_id="E-2", department=self.dept)

        # Intern 1 (Assigned to Supervisor 1)
        self.int1_user = User.objects.create_user(email="i1@example.com", password="Password@123", role="INTERN")
        self.int1 = InternProfile.objects.create(user=self.int1_user, intern_id="DMK-INT-101")
        self.ship1 = Internship.objects.create(
            intern=self.int1, supervisor=self.sup1, department=self.dept, position="Intern 1",
            start_date=date(2026, 8, 3), expected_end_date=date(2026, 8, 28)
        )
        self.att1 = Attendance.objects.create(intern=self.int1, date=date(2026, 8, 3), status=AttendanceStatus.PRESENT)

        # Intern 2 (Assigned to Supervisor 2)
        self.int2_user = User.objects.create_user(email="i2@example.com", password="Password@123", role="INTERN")
        self.int2 = InternProfile.objects.create(user=self.int2_user, intern_id="DMK-INT-102")
        self.ship2 = Internship.objects.create(
            intern=self.int2, supervisor=self.sup2, department=self.dept, position="Intern 2",
            start_date=date(2026, 8, 3), expected_end_date=date(2026, 8, 28)
        )
        self.att2 = Attendance.objects.create(intern=self.int2, date=date(2026, 8, 3), status=AttendanceStatus.PRESENT)

    # ─── MODEL TESTS ─────────────────────────────────────────────────────────

    def test_01_daily_log_creation(self):
        """1. Daily log creation works."""
        log = DailyLog.objects.create(
            intern=self.int1, date=date(2026, 8, 4), title="Testing", description="Desc", hours_worked=5.0
        )
        self.assertEqual(log.status, DailyLogStatus.PENDING)

    def test_02_duplicate_intern_date_rejected(self):
        """2. Duplicate intern/date is rejected."""
        DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T1", description="D1", hours_worked=5)
        with self.assertRaises((ValidationError, IntegrityError)):
            DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T2", description="D2", hours_worked=4)

    def test_03_invalid_hours_rejected(self):
        """3. Invalid hours (<=0 or >24) are rejected."""
        with self.assertRaises(ValidationError):
            DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T1", description="D1", hours_worked=0)
        with self.assertRaises(ValidationError):
            DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T1", description="D1", hours_worked=25)

    def test_04_date_before_internship_rejected(self):
        """4. Date before internship is rejected."""
        with self.assertRaises(ValidationError):
            DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 1), title="T1", description="D1", hours_worked=5)

    def test_05_date_after_internship_rejected(self):
        """5. Date after internship is rejected."""
        with self.assertRaises(ValidationError):
            DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 31), title="T1", description="D1", hours_worked=5)

    def test_06_weekend_log_rejected(self):
        """6. Weekend log is rejected."""
        # Aug 8, 2026 is Saturday
        with self.assertRaises(ValidationError):
            DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 8), title="T1", description="D1", hours_worked=5)


    # ─── INTERN WORKFLOW TESTS ───────────────────────────────────────────────

    def test_07_intern_can_create_own_log(self):
        """7. Intern can create own log."""
        self.client.login(username="i1@example.com", password="Password@123")
        response = self.client.post(reverse('logbook:intern_create'), {
            'date': '2026-08-05', 'title': 'My task', 'description': 'desc', 'hours_worked': 8
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DailyLog.objects.filter(intern=self.int1, date=date(2026, 8, 5)).exists())

    def test_08_intern_can_view_own_log(self):
        """8. Intern can view own log."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="My task", description="desc", hours_worked=8)
        self.client.login(username="i1@example.com", password="Password@123")
        response = self.client.get(reverse('logbook:intern_detail', kwargs={'pk': log.pk}))
        self.assertEqual(response.status_code, 200)

    def test_09_intern_cannot_view_another_interns_log(self):
        """9. Intern cannot view another intern's log."""
        log2 = DailyLog.objects.create(intern=self.int2, date=date(2026, 8, 4), title="Int2 task", description="desc", hours_worked=8)
        self.client.login(username="i1@example.com", password="Password@123")
        response = self.client.get(reverse('logbook:intern_detail', kwargs={'pk': log2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_10_intern_can_edit_pending_log(self):
        """10. Intern can edit pending log."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="Old title", description="desc", hours_worked=8)
        self.client.login(username="i1@example.com", password="Password@123")
        response = self.client.post(reverse('logbook:intern_edit', kwargs={'pk': log.pk}), {
            'date': '2026-08-04', 'title': 'New title', 'description': 'desc', 'hours_worked': 8
        })
        self.assertEqual(response.status_code, 302)
        log.refresh_from_db()
        self.assertEqual(log.title, "New title")

    def test_11_intern_cannot_edit_approved_log(self):
        """11. Intern cannot edit approved log."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="Title", description="desc", hours_worked=8, status=DailyLogStatus.APPROVED)
        self.client.login(username="i1@example.com", password="Password@123")
        response = self.client.post(reverse('logbook:intern_edit', kwargs={'pk': log.pk}), {
            'date': '2026-08-04', 'title': 'New title', 'description': 'desc', 'hours_worked': 8
        })
        # View redirects away without saving
        self.assertEqual(response.status_code, 302)
        log.refresh_from_db()
        self.assertEqual(log.title, "Title")

    def test_12_intern_can_edit_rejected_log(self):
        """12. Intern can edit rejected log."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="Title", description="desc", hours_worked=8, status=DailyLogStatus.REJECTED)
        self.client.login(username="i1@example.com", password="Password@123")
        response = self.client.get(reverse('logbook:intern_edit', kwargs={'pk': log.pk}))
        self.assertEqual(response.status_code, 200)

    def test_13_intern_can_resubmit_rejected_log(self):
        """13. Intern can resubmit rejected log (status becomes PENDING)."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="Title", description="desc", hours_worked=8, status=DailyLogStatus.REJECTED)
        self.client.login(username="i1@example.com", password="Password@123")
        self.client.post(reverse('logbook:intern_edit', kwargs={'pk': log.pk}), {
            'date': '2026-08-04', 'title': 'Fixed title', 'description': 'desc', 'hours_worked': 8
        })
        log.refresh_from_db()
        self.assertEqual(log.status, DailyLogStatus.PENDING)

    def test_14_intern_cannot_manually_approve(self):
        """14. Intern cannot manually approve a log."""
        self.client.login(username="i1@example.com", password="Password@123")
        self.client.post(reverse('logbook:intern_create'), {
            'date': '2026-08-05', 'title': 'Task', 'description': 'desc', 'hours_worked': 8, 'status': 'APPROVED'
        })
        log = DailyLog.objects.get(intern=self.int1, date=date(2026, 8, 5))
        self.assertEqual(log.status, DailyLogStatus.PENDING)

    def test_15_intern_cannot_modify_supervisor_feedback(self):
        """15. Intern cannot modify supervisor feedback."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T", description="D", hours_worked=8, status=DailyLogStatus.REJECTED, supervisor_feedback="Bad")
        self.client.login(username="i1@example.com", password="Password@123")
        self.client.post(reverse('logbook:intern_edit', kwargs={'pk': log.pk}), {
            'date': '2026-08-04', 'title': 'T2', 'description': 'D', 'hours_worked': 8, 'supervisor_feedback': 'Changed'
        })
        log.refresh_from_db()
        self.assertEqual(log.supervisor_feedback, "Bad")


    # ─── SUPERVISOR WORKFLOW TESTS ───────────────────────────────────────────

    def test_16_supervisor_can_view_assigned_interns_logs(self):
        """16. Supervisor can view assigned interns' logs."""
        DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T", description="D", hours_worked=8)
        self.client.login(username="s1@example.com", password="Password@123")
        response = self.client.get(reverse('logbook:supervisor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DMK-INT-101")

    def test_17_supervisor_cannot_view_another_supervisors_logs(self):
        """17. Supervisor cannot view another supervisor's intern logs."""
        log2 = DailyLog.objects.create(intern=self.int2, date=date(2026, 8, 4), title="T", description="D", hours_worked=8)
        self.client.login(username="s1@example.com", password="Password@123")
        response = self.client.get(reverse('logbook:supervisor_detail', kwargs={'pk': log2.pk}))
        self.assertEqual(response.status_code, 403)

    def test_18_supervisor_can_approve_pending_log(self):
        """18. Supervisor can approve pending log."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T", description="D", hours_worked=8)
        self.client.login(username="s1@example.com", password="Password@123")
        self.client.post(reverse('logbook:supervisor_approve', kwargs={'pk': log.pk}), {'feedback': 'Good job'})
        log.refresh_from_db()
        self.assertEqual(log.status, DailyLogStatus.APPROVED)
        self.assertEqual(log.supervisor_feedback, 'Good job')

    def test_19_supervisor_can_reject_pending_log(self):
        """19. Supervisor can reject pending log."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T", description="D", hours_worked=8)
        self.client.login(username="s1@example.com", password="Password@123")
        self.client.post(reverse('logbook:supervisor_reject', kwargs={'pk': log.pk}), {'feedback': 'Fix this'})
        log.refresh_from_db()
        self.assertEqual(log.status, DailyLogStatus.REJECTED)

    def test_20_rejection_requires_feedback(self):
        """20. Rejection requires feedback."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T", description="D", hours_worked=8)
        self.client.login(username="s1@example.com", password="Password@123")
        response = self.client.post(reverse('logbook:supervisor_reject', kwargs={'pk': log.pk}), {'feedback': ''})
        # Stays pending since feedback was missing
        log.refresh_from_db()
        self.assertEqual(log.status, DailyLogStatus.PENDING)

    def test_21_supervisor_feedback_visible_to_intern(self):
        """21. Supervisor feedback is visible to intern."""
        log = DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T", description="D", hours_worked=8, status=DailyLogStatus.REJECTED, supervisor_feedback="Needs detail")
        self.client.login(username="i1@example.com", password="Password@123")
        response = self.client.get(reverse('logbook:intern_detail', kwargs={'pk': log.pk}))
        self.assertContains(response, "Needs detail")


    # ─── DASHBOARD & SECURITY TESTS ──────────────────────────────────────────

    def test_22_intern_log_statistics(self):
        """22. Intern log statistics are correct."""
        DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T1", description="D1", hours_worked=5, status=DailyLogStatus.APPROVED)
        DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 5), title="T2", description="D2", hours_worked=3, status=DailyLogStatus.PENDING)

        self.client.login(username="i1@example.com", password="Password@123")
        response = self.client.get(reverse('intern_dashboard'))
        self.assertContains(response, "Total Logs: 2")
        self.assertContains(response, "8")  # Total hours

    def test_23_supervisor_pending_log_count(self):
        """23. Supervisor pending log count is correct."""
        DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 4), title="T1", description="D1", hours_worked=5, status=DailyLogStatus.PENDING)
        DailyLog.objects.create(intern=self.int1, date=date(2026, 8, 5), title="T2", description="D2", hours_worked=3, status=DailyLogStatus.APPROVED)

        self.client.login(username="s1@example.com", password="Password@123")
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertContains(response, "1 Pending")

    def test_24_unauthenticated_access_rejected(self):
        """24. Unauthenticated users cannot access logbook pages."""
        response = self.client.get(reverse('logbook:intern_list'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('logbook:supervisor_list'))
        self.assertEqual(response.status_code, 302)
