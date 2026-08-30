from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """
    Department model representing municipality departments.
    """
    name = models.CharField(_('department name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        ordering = ['name']

    def __str__(self):
        return self.name


class SupervisorProfile(models.Model):
    """
    Supervisor profile connected 1-to-1 with custom User model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supervisor_profile',
        limit_choices_to={'role': 'SUPERVISOR'}
    )
    employee_id = models.CharField(_('employee ID'), max_length=50, unique=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    position = models.CharField(_('position / designation'), max_length=100, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervisors'
    )
    profile_photo = models.ImageField(
        upload_to='profiles/supervisors/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('supervisor profile')
        verbose_name_plural = _('supervisor profiles')
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


class InternProfile(models.Model):
    """
    Intern profile connected 1-to-1 with custom User model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='intern_profile',
        limit_choices_to={'role': 'INTERN'}
    )
    intern_id = models.CharField(_('intern ID'), max_length=50, unique=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    college = models.CharField(_('college / university'), max_length=200, blank=True)
    program = models.CharField(_('program / degree'), max_length=100, blank=True)
    semester_or_year = models.CharField(_('semester / year'), max_length=50, blank=True)
    address = models.CharField(_('address'), max_length=255, blank=True)
    profile_photo = models.ImageField(
        upload_to='profiles/interns/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('intern profile')
        verbose_name_plural = _('intern profiles')
        ordering = ['intern_id']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.intern_id})"

    @classmethod
    def generate_next_intern_id(cls):
        """Generates the next unique intern ID format: DMK-INT-001"""
        count = cls.objects.count() + 1
        new_id = f"DMK-INT-{count:03d}"
        while cls.objects.filter(intern_id=new_id).exists():
            count += 1
            new_id = f"DMK-INT-{count:03d}"
        return new_id


class InternshipStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    ACTIVE = 'ACTIVE', _('Active')
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELLED = 'CANCELLED', _('Cancelled')


class Internship(models.Model):
    """
    Internship record linking an InternProfile to a SupervisorProfile & Department.
    V1 assumes one active/current internship per intern profile.
    """
    intern = models.OneToOneField(
        InternProfile,
        on_delete=models.CASCADE,
        related_name='internship'
    )
    supervisor = models.ForeignKey(
        SupervisorProfile,
        on_delete=models.PROTECT,
        related_name='assigned_internships'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='internships'
    )
    position = models.CharField(_('position / role'), max_length=100)
    start_date = models.DateField(_('start date'))
    expected_end_date = models.DateField(_('expected end date'))
    actual_end_date = models.DateField(_('actual end date'), null=True, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=InternshipStatus.choices,
        default=InternshipStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('internship')
        verbose_name_plural = _('internships')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.intern.user.get_full_name()} - {self.department.name} ({self.status})"

    def clean(self):
        super().clean()
        if self.start_date and self.expected_end_date:
            if self.expected_end_date < self.start_date:
                raise ValidationError({
                    'expected_end_date': _('Expected end date cannot be earlier than start date.')
                })
        if self.start_date and self.actual_end_date:
            if self.actual_end_date < self.start_date:
                raise ValidationError({
                    'actual_end_date': _('Actual end date cannot be earlier than start date.')
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
