"""
Logbook forms for Damak Municipality IMS.
Phase 5: Daily Logbook / Activity Tracking.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import DailyLog, DailyLogStatus


class DailyLogForm(forms.ModelForm):
    """
    Intern-facing form for creating and editing daily log entries.

    Excludes:
        - intern   (set from request.user.intern_profile in the view)
        - status   (always set to PENDING on create; PENDING on resubmit)
        - supervisor_feedback  (read-only to interns)
    """

    class Meta:
        model = DailyLog
        fields = ['date', 'title', 'description', 'skills_learned', 'challenges', 'hours_worked']
        widgets = {
            'date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Website Development, Database Design …',
                'maxlength': 255,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe what you worked on today …',
            }),
            'skills_learned': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Skills, tools, or concepts you practiced today …',
            }),
            'challenges': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Difficulties faced, blockers, or open questions …',
            }),
            'hours_worked': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.5',
                'max': '24',
                'step': '0.5',
                'placeholder': 'e.g. 6',
            }),
        }
        labels = {
            'title': _('Activity Title'),
            'description': _('Description / Activities Performed'),
            'skills_learned': _('Skills Learned (optional)'),
            'challenges': _('Problems / Challenges (optional)'),
            'hours_worked': _('Hours Worked'),
        }

    def __init__(self, *args, intern_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._intern_profile = intern_profile
        # Make date input show correct format for pre-filled values
        if self.instance and self.instance.pk and self.instance.date:
            self.initial['date'] = self.instance.date.strftime('%Y-%m-%d')

    def clean_hours_worked(self):
        hours = self.cleaned_data.get('hours_worked')
        if hours is not None:
            if hours <= 0:
                raise forms.ValidationError(_('Hours worked must be greater than 0.'))
            if hours > 24:
                raise forms.ValidationError(_('Hours worked cannot exceed 24 hours per day.'))
        return hours

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date is None:
            return date

        # Weekend check
        if date.weekday() >= 5:
            day_name = date.strftime('%A')
            raise forms.ValidationError(
                _(f'Daily logs cannot be submitted for weekends. '
                  f'{date.strftime("%B %d, %Y")} is a {day_name}.')
            )

        # Internship boundary check
        if self._intern_profile:
            internship = getattr(self._intern_profile, 'internship', None)
            if internship:
                if date < internship.start_date:
                    raise forms.ValidationError(
                        _(f'Log date cannot be before your internship start date '
                          f'({internship.start_date.strftime("%B %d, %Y")}).')
                    )
                end_boundary = internship.actual_end_date or internship.expected_end_date
                if date > end_boundary:
                    raise forms.ValidationError(
                        _(f'Log date cannot be after your internship end date '
                          f'({end_boundary.strftime("%B %d, %Y")}).')
                    )
        return date

    def validate_unique(self):
        """
        Check unique intern+date constraint and show friendly message.
        Called automatically by ModelForm.
        """
        super().validate_unique()

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class SupervisorFeedbackForm(forms.Form):
    """
    Minimal form used by supervisor to submit feedback when approving/rejecting a log.
    """
    feedback = forms.CharField(
        label=_('Supervisor Feedback'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Provide your feedback on this daily log entry …',
        }),
        required=False,
    )

    def clean_feedback(self):
        return self.cleaned_data.get('feedback', '').strip()
