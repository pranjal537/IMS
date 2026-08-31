from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Attendance, AttendanceStatus


class SupervisorAttendanceForm(forms.ModelForm):
    """
    Form for supervisors/staff to record or edit intern attendance records.
    Allows changing status (PRESENT, LEAVE, ABSENT), check-in, check-out, and remarks.
    """
    class Meta:
        model = Attendance
        fields = ['intern', 'date', 'status', 'check_in', 'check_out', 'remarks']
        widgets = {
            'intern': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'check_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional remarks...'}),
        }

    def __init__(self, *args, supervisor_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if supervisor_profile:
            # Limit intern selection to interns assigned to this supervisor
            from interns.models import InternProfile
            assigned_intern_ids = supervisor_profile.assigned_internships.values_list('intern_id', flat=True)
            self.fields['intern'].queryset = InternProfile.objects.filter(id__in=assigned_intern_ids)
