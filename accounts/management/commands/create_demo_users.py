"""
Management command to create demo users and Phase 3 demo data for local development and testing.

Usage:
    python manage.py create_demo_users

Demo accounts created:
    Supervisor: supervisor@example.com  / DamakIMS@2026
    Intern:     intern@example.com      / DamakIMS@2026

IMPORTANT:
    These are LOCAL DEVELOPMENT accounts only.
    Do NOT use these credentials or this command in production.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date
import os

from interns.models import Department, SupervisorProfile, InternProfile, Internship, InternshipStatus

User = get_user_model()
DEFAULT_DEMO_PASSWORD = 'DamakIMS@2026'


class Command(BaseCommand):
    help = (
        'Creates demo Supervisor and Intern users along with Phase 3 profiles and internship data. '
        'Do NOT run this command in a production environment.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default=None,
            help='Override the demo password (default: DamakIMS@2026)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset passwords of existing demo users instead of skipping them.',
        )

    def handle(self, *args, **options):
        demo_password = (
            options.get('password')
            or os.environ.get('DEMO_PASSWORD')
            or DEFAULT_DEMO_PASSWORD
        )

        self.stdout.write(self.style.WARNING(
            '\n[NOTICE] Creating DEMO users & Phase 3 data for local development only.\n'
        ))

        # 1. Seed Departments
        dept_names = ['Information Technology', 'Finance', 'Administration', 'Engineering']
        departments = {}
        for name in dept_names:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': f'{name} Department of Damak Municipality'}
            )
            departments[name] = dept
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [CREATED] Department: {name}'))

        # 2. Create Supervisor User & Profile
        sup_user, sup_created = self._create_or_update_user(
            email='supervisor@example.com',
            first_name='Ramesh',
            last_name='Adhikari',
            role='SUPERVISOR',
            password=demo_password,
            reset=options.get('reset', False),
        )

        sup_profile, _ = SupervisorProfile.objects.get_or_create(
            user=sup_user,
            defaults={
                'employee_id': 'EMP-SUP-001',
                'phone': '+977-9852012345',
                'position': 'Senior IT Officer',
                'department': departments['Information Technology'],
            }
        )

        # 3. Create Intern User & Profile
        int_user, int_created = self._create_or_update_user(
            email='intern@example.com',
            first_name='Aayush',
            last_name='Sharma',
            role='INTERN',
            password=demo_password,
            reset=options.get('reset', False),
        )

        int_profile, _ = InternProfile.objects.get_or_create(
            user=int_user,
            defaults={
                'intern_id': 'DMK-INT-001',
                'phone': '+977-9812345678',
                'college': 'Damak Multiple Campus',
                'program': 'Bachelor of Information Technology (BIT)',
                'semester_or_year': '7th Semester',
                'address': 'Damak-6, Jhapa, Koshi Province',
            }
        )

        # 4. Create Active Internship
        internship, int_record_created = Internship.objects.get_or_create(
            intern=int_profile,
            defaults={
                'supervisor': sup_profile,
                'department': departments['Information Technology'],
                'position': 'Software & Systems Intern',
                'start_date': date(2026, 8, 1),
                'expected_end_date': date(2026, 10, 31),
                'status': InternshipStatus.ACTIVE,
            }
        )
        if int_record_created:
            self.stdout.write(self.style.SUCCESS('  [CREATED] Internship placement: DMK-INT-001 -> IT Department'))

        self.stdout.write(self.style.SUCCESS('\nDemo user setup complete.\n'))
        self.stdout.write('-' * 60)
        self.stdout.write(f'  Supervisor: supervisor@example.com  /  {demo_password}')
        self.stdout.write(f'  Intern:     intern@example.com      /  {demo_password}')
        self.stdout.write('-' * 60 + '\n')

    def _create_or_update_user(self, email, first_name, last_name, role, password, reset):
        try:
            user = User.objects.get(email=email)
            if reset:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  [UPDATED] Reset password for user: {email}'))
            else:
                self.stdout.write(self.style.WARNING(f'  [SKIPPED] User already exists: {email}'))
            return user, False
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f'  [CREATED] Role {role}: {email}'))
            return user, True
