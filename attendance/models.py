from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', _('Present')
    LEAVE = 'LEAVE', _('Leave')
    ABSENT = 'ABSENT', _('Absent')


class Attendance(models.Model):
    """
    Attendance record tracking daily intern check-in, check-out, status, and remarks.
    Unique constraint: intern + date must be unique.
    """
    intern = models.ForeignKey(
        'interns.InternProfile',
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(_('attendance date'))
    check_in = models.TimeField(_('check-in time'), null=True, blank=True)
    check_out = models.TimeField(_('check-out time'), null=True, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT
    )
    remarks = models.TextField(_('remarks'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('attendance record')
        verbose_name_plural = _('attendance records')
        ordering = ['-date', '-check_in']
        constraints = [
            models.UniqueConstraint(
                fields=['intern', 'date'],
                name='unique_intern_date_attendance'
            )
        ]

    def __str__(self):
        return f"{self.intern.user.get_full_name()} - {self.date} ({self.status})"

    def clean(self):
        super().clean()

        # 1. Check-out cannot be earlier than check-in
        if self.check_in and self.check_out:
            if self.check_out < self.check_in:
                raise ValidationError({
                    'check_out': _('Check-out time cannot be earlier than check-in time.')
                })

        # 2. Check internship relationship & placement dates
        if hasattr(self, 'intern') and self.intern:
            internship = getattr(self.intern, 'internship', None)
            if not internship:
                raise ValidationError({
                    'intern': _('Intern does not have an active internship placement.')
                })

            if self.date:
                if self.date < internship.start_date:
                    raise ValidationError({
                        'date': _('Attendance date cannot be before the internship start date.')
                    })
                end_boundary = internship.actual_end_date or internship.expected_end_date
                if self.date > end_boundary:
                    raise ValidationError({
                        'date': _('Attendance date cannot be after the internship end date.')
                    })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
