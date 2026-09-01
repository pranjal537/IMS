from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

from accounts.models import User, UserRole
from interns.models import InternProfile, SupervisorProfile, Department, Internship
from tasks.models import Task, TaskStatus, TaskPriority

class TaskManagementTests(TestCase):
    def setUp(self):
        # Create users
        self.supervisor_user = User.objects.create_user(
            email='supervisor@test.com', password='password123', role=UserRole.SUPERVISOR
        )
        self.intern_user = User.objects.create_user(
            email='intern@test.com', password='password123', role=UserRole.INTERN
        )
        self.other_supervisor = User.objects.create_user(
            email='other_sup@test.com', password='password123', role=UserRole.SUPERVISOR
        )
        self.other_intern = User.objects.create_user(
            email='other_intern@test.com', password='password123', role=UserRole.INTERN
        )

        # Create profiles and department
        self.dept = Department.objects.create(name='IT Department')
        self.supervisor = SupervisorProfile.objects.create(user=self.supervisor_user, department=self.dept, employee_id='EMP-01')
        self.other_sup_profile = SupervisorProfile.objects.create(user=self.other_supervisor, department=self.dept, employee_id='EMP-02')
        
        self.intern = InternProfile.objects.create(user=self.intern_user, intern_id='INT-001')
        self.intern2 = InternProfile.objects.create(user=self.other_intern, intern_id='INT-002')

        # Create internships (assign intern to supervisor, intern2 to other_sup)
        self.internship = Internship.objects.create(
            intern=self.intern,
            supervisor=self.supervisor,
            department=self.dept,
            start_date=timezone.now().date(),
            expected_end_date=timezone.now().date() + timedelta(days=90)
        )
        self.internship2 = Internship.objects.create(
            intern=self.intern2,
            supervisor=self.other_sup_profile,
            department=self.dept,
            start_date=timezone.now().date(),
            expected_end_date=timezone.now().date() + timedelta(days=90)
        )

        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

    # MODEL TESTS
    def test_task_creation(self):
        task = Task.objects.create(
            title='Test Task',
            description='Description',
            intern=self.intern,
            assigned_by=self.supervisor,
            start_date=self.today,
            due_date=self.tomorrow,
        )
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.progress, 0)
        self.assertFalse(task.is_overdue)

    def test_invalid_progress(self):
        task = Task(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                    start_date=self.today, due_date=self.tomorrow, progress=150)
        with self.assertRaises(ValidationError):
            task.clean()

    def test_negative_progress(self):
        task = Task(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                    start_date=self.today, due_date=self.tomorrow, progress=-10)
        with self.assertRaises(ValidationError):
            task.clean()

    def test_due_date_before_start_date(self):
        task = Task(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                    start_date=self.tomorrow, due_date=self.today)
        with self.assertRaises(ValidationError):
            task.clean()

    # STATUS LOGIC TESTS
    def test_progress_100_sets_completed(self):
        task = Task.objects.create(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                                   start_date=self.today, due_date=self.tomorrow)
        task.progress = 100
        task.save()
        self.assertEqual(task.status, TaskStatus.COMPLETED)

    def test_completed_task_not_overdue(self):
        task = Task.objects.create(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                                   start_date=self.yesterday - timedelta(days=2), due_date=self.yesterday,
                                   progress=100) # triggers completed
        self.assertFalse(task.is_overdue)

    def test_incomplete_past_due_task_is_overdue(self):
        task = Task.objects.create(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                                   start_date=self.yesterday - timedelta(days=2), due_date=self.yesterday,
                                   progress=50)
        self.assertTrue(task.is_overdue)
        self.assertEqual(task.display_status, TaskStatus.OVERDUE)

    def test_in_progress_can_be_updated(self):
        task = Task.objects.create(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                                   start_date=self.today, due_date=self.tomorrow, status=TaskStatus.IN_PROGRESS, progress=50)
        task.progress = 60
        task.save()
        self.assertEqual(task.progress, 60)

    # VIEW TESTS - SECURITY AND PERMISSIONS
    def test_unauthenticated_access_denied(self):
        response = self.client.get(reverse('intern_task_list'))
        self.assertEqual(response.status_code, 302)

    def test_supervisor_can_view_assigned_tasks(self):
        self.client.force_login(self.supervisor_user)
        response = self.client.get(reverse('supervisor_task_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_supervisor_cannot_view_other_supervisor_tasks(self):
        task = Task.objects.create(title='Other Task', description='B', intern=self.intern2, assigned_by=self.other_sup_profile,
                                   start_date=self.today, due_date=self.tomorrow)
        self.client.force_login(self.supervisor_user)
        response = self.client.get(reverse('supervisor_task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 404)

    def test_intern_can_view_own_tasks(self):
        self.client.force_login(self.intern_user)
        response = self.client.get(reverse('intern_task_list'))
        self.assertEqual(response.status_code, 200)

    def test_intern_cannot_view_other_intern_tasks(self):
        task = Task.objects.create(title='Other Task', description='B', intern=self.intern2, assigned_by=self.other_sup_profile,
                                   start_date=self.today, due_date=self.tomorrow)
        self.client.force_login(self.intern_user)
        response = self.client.get(reverse('intern_task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 404)

    def test_supervisor_create_task(self):
        self.client.force_login(self.supervisor_user)
        response = self.client.post(reverse('supervisor_task_create'), {
            'title': 'New Task',
            'description': 'Work hard',
            'intern': self.intern.pk,
            'priority': TaskPriority.HIGH,
            'start_date': self.today.strftime('%Y-%m-%d'),
            'due_date': self.tomorrow.strftime('%Y-%m-%d'),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)

    def test_supervisor_cannot_create_task_for_unassigned_intern(self):
        self.client.force_login(self.supervisor_user)
        response = self.client.post(reverse('supervisor_task_create'), {
            'title': 'Bad Task',
            'description': 'Work hard',
            'intern': self.intern2.pk, # Unassigned
            'priority': TaskPriority.HIGH,
            'start_date': self.today.strftime('%Y-%m-%d'),
            'due_date': self.tomorrow.strftime('%Y-%m-%d'),
        })
        self.assertEqual(Task.objects.count(), 0) # Form should be invalid

    def test_intern_update_progress(self):
        task = Task.objects.create(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                                   start_date=self.today, due_date=self.tomorrow)
        self.client.force_login(self.intern_user)
        response = self.client.post(reverse('intern_task_update', args=[task.pk]), {
            'progress': 50,
            'status': TaskStatus.IN_PROGRESS
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.progress, 50)
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)

    def test_intern_update_progress_100_completes_task(self):
        task = Task.objects.create(title='A', description='B', intern=self.intern, assigned_by=self.supervisor,
                                   start_date=self.today, due_date=self.tomorrow)
        self.client.force_login(self.intern_user)
        response = self.client.post(reverse('intern_task_update', args=[task.pk]), {
            'progress': 100,
            'status': TaskStatus.IN_PROGRESS
        })
        task.refresh_from_db()
        self.assertEqual(task.progress, 100)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
