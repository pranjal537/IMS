from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Department, SupervisorProfile, InternProfile, Internship


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Information Technology'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department description...'}),
        }


class SupervisorProfileEditForm(forms.ModelForm):
    """
    Form for supervisors to update their own profile (phone, position, profile_photo).
    Employee ID and Department are read-only / immutable by supervisor.
    """
    class Meta:
        model = SupervisorProfile
        fields = ['phone', 'position', 'profile_photo']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+977 9800000000'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Senior IT Officer'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class InternProfileEditForm(forms.ModelForm):
    """
    Form for interns to update their personal info.
    Protected fields (intern_id, supervisor, department, status) cannot be changed here.
    """
    class Meta:
        model = InternProfile
        fields = ['phone', 'address', 'college', 'program', 'semester_or_year', 'profile_photo']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+977 9800000000'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Damak-5, Jhapa'}),
            'college': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tribhuvan University'}),
            'program': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'BIT / BSc CSIT / BE'}),
            'semester_or_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '7th Semester'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class InternshipForm(forms.ModelForm):
    """
    Form for management to create/edit internships.
    """
    class Meta:
        model = Internship
        fields = ['intern', 'supervisor', 'department', 'position', 'start_date', 'expected_end_date', 'actual_end_date', 'status']
        widgets = {
            'intern': forms.Select(attrs={'class': 'form-select'}),
            'supervisor': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Software Engineering Intern'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
