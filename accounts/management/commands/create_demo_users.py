"""
Management command to create demo users for local development and testing.

Usage:
    python manage.py create_demo_users

Demo accounts created:
    Supervisor: supervisor@example.com  / DamakIMS@2026
    Intern:     intern@example.com      / DamakIMS@2026

IMPORTANT:
    These are LOCAL DEVELOPMENT accounts only.
    Do NOT use these credentials or this command in production.
    Change the demo password via the DEMO_PASSWORD env variable or
    by editing the users in Django admin after creation.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

DEFAULT_DEMO_PASSWORD = 'DamakIMS@2026'


class Command(BaseCommand):
    help = (
        'Creates demo Supervisor and Intern users for local development. '
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
            '\n[NOTICE] Creating DEMO users for local development only. '
            'Do not use in production.\n'
        ))

        # ── Supervisor Demo User ──────────────────────────────────────────
        self._create_or_update_user(
            email='supervisor@example.com',
            first_name='Ramesh',
            last_name='Adhikari',
            role='SUPERVISOR',
            password=demo_password,
            reset=options.get('reset', False),
        )

        # ── Intern Demo User ─────────────────────────────────────────────
        self._create_or_update_user(
            email='intern@example.com',
            first_name='Aayush',
            last_name='Sharma',
            role='INTERN',
            password=demo_password,
            reset=options.get('reset', False),
        )

        self.stdout.write(self.style.SUCCESS('\nDemo user setup complete.\n'))
        self.stdout.write('-' * 60)
        self.stdout.write(
            f'  Supervisor: supervisor@example.com  /  {demo_password}'
        )
        self.stdout.write(
            f'  Intern:     intern@example.com      /  {demo_password}'
        )
        self.stdout.write('-' * 60 + '\n')

    def _create_or_update_user(self, email, first_name, last_name, role, password, reset):
        try:
            user = User.objects.get(email=email)
            if reset:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'  [UPDATED] Reset password for user: {email}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  [SKIPPED] User already exists: {email}')
                )
        except User.DoesNotExist:
            User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f'  [CREATED] Role {role}: {email}')
            )
