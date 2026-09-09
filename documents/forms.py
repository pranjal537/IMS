import os
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Document, DocumentCategory
from interns.models import InternProfile


ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class DocumentUploadForm(forms.ModelForm):
    intern = forms.ModelChoiceField(
        queryset=InternProfile.objects.none(),
        required=False,
        label=_('Intern'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Document
        fields = ['title', 'category', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter document title (e.g. Citizenship Certificate)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description or notes about this document...'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        assigned_interns = kwargs.pop('assigned_interns', None)
        super().__init__(*args, **kwargs)

        if assigned_interns is not None:
            self.fields['intern'].queryset = assigned_interns
            self.fields['intern'].required = True
        else:
            self.fields.pop('intern', None)

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')

        if not uploaded_file:
            raise ValidationError(_('Please select a file to upload.'))

        # Check empty file
        if uploaded_file.size == 0:
            raise ValidationError(_('The uploaded file is empty.'))

        # Check file size (10 MB max)
        if uploaded_file.size > MAX_FILE_SIZE_BYTES:
            size_mb = round(uploaded_file.size / (1024 * 1024), 2)
            raise ValidationError(_(f'File size ({size_mb} MB) exceeds the maximum allowed limit of 10 MB.'))

        # Check file extension
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed_list = ', '.join(sorted(ALLOWED_EXTENSIONS))
            raise ValidationError(_(f'File format "{ext}" is not supported. Allowed formats are: {allowed_list}.'))

        return uploaded_file
