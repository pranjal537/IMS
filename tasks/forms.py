from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Task, TaskStatus
from interns.models import InternProfile

class SupervisorTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'intern', 'priority', 'start_date', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'intern': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, supervisor_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if supervisor_profile:
            self.fields['intern'].queryset = InternProfile.objects.filter(
                internship__supervisor=supervisor_profile
            ).select_related('user')
        if self.instance and self.instance.pk:
            if self.instance.start_date:
                self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%d')
            if self.instance.due_date:
                self.initial['due_date'] = self.instance.due_date.strftime('%Y-%m-%d')

class SupervisorTaskEditForm(SupervisorTaskForm):
    class Meta(SupervisorTaskForm.Meta):
        fields = SupervisorTaskForm.Meta.fields + ['supervisor_comment']
        widgets = {
            **SupervisorTaskForm.Meta.widgets,
            'supervisor_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InternTaskProgressForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['progress', 'status']
        widgets = {
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude OVERDUE from choices since intern shouldn't manually set it to OVERDUE
        self.fields['status'].choices = [
            choice for choice in TaskStatus.choices if choice[0] != TaskStatus.OVERDUE
        ]
