"""
Logbook models for Damak Municipality IMS.
Phase 5: Daily Logbook / Activity Tracking.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class DailyLogStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    APPROVED = 'APPROVED', _('Approved')
    REJECTED = 'REJECTED', _('Rejected')


class DailyLog(models.Model):
    """
    Daily activity log submitted by an intern.

    Relationships:
        DailyLog → InternProfile → Internship → SupervisorProfile

    Status lifecycle:
        PENDING  →  APPROVED   (supervisor approves)
        PENDING  →  REJECTED   (supervisor rejects; feedback required)
        REJECTED →  PENDING    (intern resubmits after editing)
    """

    intern = models.ForeignKey(
        'interns.InternProfile',
        on_delete=models.CASCADE,
        related_name='daily_logs',
        verbose_name=_('intern'),
    )
    date = models.DateField(_('log date'))
    title = models.CharField(_('activity title'), max_length=255)
    description = models.TextField(_('description / activities performed'))
    skills_learned = models.TextField(_('skills learned'), blank=True)
    challenges = models.TextField(_('problems / challenges'), blank=True)
    hours_worked = models.DecimalField(
        _('hours worked'),
        max_digits=4,
        decimal_places=1,
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=DailyLogStatus.choices,
        default=DailyLogStatus.PENDING,
    )
    supervisor_feedback = models.TextField(
        _('supervisor feedback'),
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('daily log')
        verbose_name_plural = _('daily logs')
        ordering = ['-date', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['intern', 'date'],
                name='unique_intern_date_dailylog'
            )
        ]

    def __str__(self):
        return f"{self.intern.user.get_full_name()} — {self.date} — {self.title[:50]}"

    def clean(self):
        super().clean()

        # 1. Hours worked must be > 0 and ≤ 24
        if self.hours_worked is not None:
            if self.hours_worked <= 0:
                raise ValidationError({
                    'hours_worked': _('Hours worked must be greater than 0.')
                })
            if self.hours_worked > 24:
                raise ValidationError({
                    'hours_worked': _('Hours worked cannot exceed 24 hours per day.')
                })

        # 2. Date and internship boundary validation
        if self.date and self.intern_id:
            internship = getattr(self.intern, 'internship', None)
            if not internship:
                raise ValidationError({
                    'intern': _('This intern does not have an active internship placement.')
                })

            # 3. Date cannot be before internship start
            if self.date < internship.start_date:
                raise ValidationError({
                    'date': _(
                        f'Log date cannot be before the internship start date '
                        f'({internship.start_date.strftime("%B %d, %Y")}).'
                    )
                })

            # 4. Date cannot be after expected end date
            end_boundary = internship.actual_end_date or internship.expected_end_date
            if self.date > end_boundary:
                raise ValidationError({
                    'date': _(
                        f'Log date cannot be after the internship end date '
                        f'({end_boundary.strftime("%B %d, %Y")}).'
                    )
                })

        # 5. No logs for Saturday (5) or Sunday (6)
        if self.date:
            if self.date.weekday() >= 5:
                day_name = self.date.strftime('%A')
                raise ValidationError({
                    'date': _(
                        f'Daily logs cannot be submitted for weekends. '
                        f'{self.date.strftime("%B %d, %Y")} is a {day_name}.'
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ── Convenience helpers ──────────────────────────────────────────────────

    @property
    def is_pending(self):
        return self.status == DailyLogStatus.PENDING

    @property
    def is_approved(self):
        return self.status == DailyLogStatus.APPROVED

    @property
    def is_rejected(self):
        return self.status == DailyLogStatus.REJECTED

    @property
    def can_intern_edit(self):
        """Intern may edit only PENDING or REJECTED logs."""
        return self.status in (DailyLogStatus.PENDING, DailyLogStatus.REJECTED)

    def get_status_badge_class(self):
        """Returns Bootstrap badge class for the current status."""
        mapping = {
            DailyLogStatus.PENDING: 'bg-warning text-dark',
            DailyLogStatus.APPROVED: 'bg-success',
            DailyLogStatus.REJECTED: 'bg-danger',
        }
        return mapping.get(self.status, 'bg-secondary')
