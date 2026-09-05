from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone

from accounts.models import UserRole
from interns.models import Department, SupervisorProfile, InternProfile, Internship, InternshipStatus
from logbook.models import DailyLog, DailyLogStatus
from attendance.models import Attendance, AttendanceStatus
from tasks.models import Task, TaskStatus
from evaluations.models import Evaluation

User = get_user_model()


class EvaluationTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Departments
        self.dept1 = Department.objects.create(name="IT")
        self.dept2 = Department.objects.create(name="HR")
        
        # Supervisors
        self.sup1_user = User.objects.create_user(email="sup1@test.com", password="password", first_name="Supervisor", last_name="One", role=UserRole.SUPERVISOR)
        self.sup1 = SupervisorProfile.objects.create(user=self.sup1_user, employee_id="EMP-1", department=self.dept1)
        
        self.sup2_user = User.objects.create_user(email="sup2@test.com", password="password", first_name="Supervisor", last_name="Two", role=UserRole.SUPERVISOR)
        self.sup2 = SupervisorProfile.objects.create(user=self.sup2_user, employee_id="EMP-2", department=self.dept2)
        
        # Interns
        self.intern1_user = User.objects.create_user(email="int1@test.com", password="password", first_name="Intern", last_name="One", role=UserRole.INTERN)
        self.intern1 = InternProfile.objects.create(user=self.intern1_user, intern_id="INT-1", college="ABC", program="CS")
        
        self.intern2_user = User.objects.create_user(email="int2@test.com", password="password", first_name="Intern", last_name="Two", role=UserRole.INTERN)
        self.intern2 = InternProfile.objects.create(user=self.intern2_user, intern_id="INT-2", college="XYZ", program="IT")
        
        # Internships
        today = timezone.now().date()
        self.internship1 = Internship.objects.create(
            intern=self.intern1, supervisor=self.sup1, department=self.dept1,
            position="Dev", start_date=today - timedelta(days=30), expected_end_date=today + timedelta(days=30), status=InternshipStatus.ACTIVE
        )
        
        self.internship2 = Internship.objects.create(
            intern=self.intern2, supervisor=self.sup2, department=self.dept2,
            position="Analyst", start_date=today - timedelta(days=30), expected_end_date=today + timedelta(days=30), status=InternshipStatus.ACTIVE
        )
        
        # Test Data for Progress
        # Attendance
        Attendance.objects.create(intern=self.intern1, date=today - timedelta(days=1), status=AttendanceStatus.PRESENT)
        # Logbook
        DailyLog.objects.create(intern=self.intern1, date=today - timedelta(days=1), title="Log", description="Log description", hours_worked=8, status=DailyLogStatus.APPROVED)
        # Tasks
        Task.objects.create(
            intern=self.intern1,
            assigned_by=self.sup1,
            title="Task",
            description="Task description",
            start_date=today - timedelta(days=5),
            due_date=today + timedelta(days=1),
            status=TaskStatus.COMPLETED,
            progress=100
        )

    # -----------------------------------------------------
    # MODEL TESTS
    # -----------------------------------------------------
    
    def test_evaluation_can_be_created(self):
        eval_obj = Evaluation.objects.create(
            internship=self.internship1,
            technical_skills=4, communication=5, punctuality=4, problem_solving=3,
            professionalism=5, work_quality=4, learning_ability=5, discipline=4,
            final_recommendation="RECOMMENDED"
        )
        self.assertEqual(Evaluation.objects.count(), 1)
        # Score calculation: sum(34) / 8 = 4.25
        self.assertEqual(eval_obj.overall_score, 4.25)
        
    def test_rating_validation(self):
        # Above 5
        eval_high = Evaluation(internship=self.internship1, technical_skills=6, communication=5, punctuality=5, problem_solving=5, professionalism=5, work_quality=5, learning_ability=5, discipline=5)
        with self.assertRaises(ValidationError):
            eval_high.full_clean()
            
        # Below 1
        eval_low = Evaluation(internship=self.internship1, technical_skills=0, communication=5, punctuality=5, problem_solving=5, professionalism=5, work_quality=5, learning_ability=5, discipline=5)
        with self.assertRaises(ValidationError):
            eval_low.full_clean()
            
    def test_duplicate_evaluation_handling(self):
        Evaluation.objects.create(
            internship=self.internship1,
            technical_skills=4, communication=4, punctuality=4, problem_solving=4,
            professionalism=4, work_quality=4, learning_ability=4, discipline=4,
            final_recommendation="RECOMMENDED"
        )
        # Creating another evaluation for the same internship should fail
        with self.assertRaises((IntegrityError, ValidationError)):
            Evaluation.objects.create(
                internship=self.internship1,
                technical_skills=3, communication=3, punctuality=3, problem_solving=3,
                professionalism=3, work_quality=3, learning_ability=3, discipline=3,
                final_recommendation="RECOMMENDED"
            )

    # -----------------------------------------------------
    # SUPERVISOR ACCESS TESTS
    # -----------------------------------------------------

    def test_supervisor_can_view_assigned_interns_evaluations(self):
        self.client.force_login(self.sup1_user)
        response = self.client.get(reverse('evaluations:supervisor_evaluation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intern1_user.get_full_name())
        self.assertNotContains(response, self.intern2_user.get_full_name())

    def test_supervisor_can_create_evaluation_for_assigned_intern(self):
        self.client.force_login(self.sup1_user)
        url = reverse('evaluations:supervisor_evaluation_create', args=[self.internship1.id])
        data = {
            'technical_skills': 5, 'communication': 5, 'punctuality': 5, 'problem_solving': 5,
            'professionalism': 5, 'work_quality': 5, 'learning_ability': 5, 'discipline': 5,
            'final_recommendation': 'HIGHLY_RECOMMENDED'
        }
        response = self.client.post(url, data)
        self.assertEqual(Evaluation.objects.count(), 1)
        self.assertEqual(Evaluation.objects.first().overall_score, 5.0)

    def test_supervisor_cannot_evaluate_unassigned_intern(self):
        self.client.force_login(self.sup1_user)
        url = reverse('evaluations:supervisor_evaluation_create', args=[self.internship2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_supervisor_can_edit_assigned_intern_evaluation(self):
        eval_obj = Evaluation.objects.create(
            internship=self.internship1,
            technical_skills=4, communication=4, punctuality=4, problem_solving=4,
            professionalism=4, work_quality=4, learning_ability=4, discipline=4,
            final_recommendation="RECOMMENDED"
        )
        self.client.force_login(self.sup1_user)
        url = reverse('evaluations:supervisor_evaluation_edit', args=[eval_obj.id])
        data = {
            'technical_skills': 5, 'communication': 5, 'punctuality': 5, 'problem_solving': 5,
            'professionalism': 5, 'work_quality': 5, 'learning_ability': 5, 'discipline': 5,
            'final_recommendation': 'HIGHLY_RECOMMENDED'
        }
        response = self.client.post(url, data)
        eval_obj.refresh_from_db()
        self.assertEqual(eval_obj.overall_score, 5.0)

    def test_supervisor_cannot_access_unassigned_evaluation(self):
        eval_obj2 = Evaluation.objects.create(
            internship=self.internship2,
            technical_skills=4, communication=4, punctuality=4, problem_solving=4,
            professionalism=4, work_quality=4, learning_ability=4, discipline=4,
            final_recommendation="RECOMMENDED"
        )
        self.client.force_login(self.sup1_user)
        url = reverse('evaluations:supervisor_evaluation_detail', args=[eval_obj2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # -----------------------------------------------------
    # INTERN ACCESS TESTS
    # -----------------------------------------------------

    def test_intern_can_view_own_evaluation(self):
        eval_obj = Evaluation.objects.create(
            internship=self.internship1,
            technical_skills=5, communication=5, punctuality=5, problem_solving=5,
            professionalism=5, work_quality=5, learning_ability=5, discipline=5,
            final_recommendation="HIGHLY_RECOMMENDED"
        )
        self.client.force_login(self.intern1_user)
        response = self.client.get(reverse('evaluations:intern_evaluation_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5.0')

    # -----------------------------------------------------
    # PROGRESS TESTS
    # -----------------------------------------------------

    def test_intern_progress_calculation(self):
        self.client.force_login(self.intern1_user)
        response = self.client.get(reverse('evaluations:intern_progress'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('time_stats', response.context)
        self.assertIn('attendance_stats', response.context)
        self.assertIn('log_stats', response.context)
        self.assertIn('task_stats', response.context)
        # Check task completion
        self.assertEqual(response.context['task_stats']['completed'], 1)
        self.assertEqual(response.context['task_stats']['avg_progress'], 100)

    # -----------------------------------------------------
    # DASHBOARD TESTS
    # -----------------------------------------------------

    def test_supervisor_evaluation_summary_on_dashboard(self):
        self.client.force_login(self.sup1_user)
        response = self.client.get(reverse('supervisor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('evaluation_stats', response.context)
        self.assertEqual(response.context['evaluation_stats']['unevaluated'], 1)
        self.assertEqual(response.context['evaluation_stats']['evaluated'], 0)

    def test_intern_evaluation_status_on_dashboard(self):
        self.client.force_login(self.intern1_user)
        response = self.client.get(reverse('intern_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('evaluation', response.context)
        self.assertIsNone(response.context['evaluation'])
