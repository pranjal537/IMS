from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from interns.models import InternProfile


class DocumentCategory(models.TextChoices):
    IDENTITY = 'IDENTITY', _('Identity / Citizenship')
    ACADEMIC = 'ACADEMIC', _('Academic Document')
    INTERNSHIP_LETTER = 'INTERNSHIP_LETTER', _('Internship Letter')
    PROJECT_REPORT = 'PROJECT_REPORT', _('Project Report')
    COMPLETION_CERT = 'COMPLETION_CERT', _('Completion Certificate')
    OTHER = 'OTHER', _('Other')


class Document(models.Model):
    intern = models.ForeignKey(
        InternProfile,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Intern')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Document Title')
    )
    category = models.CharField(
        max_length=50,
        choices=DocumentCategory.choices,
        default=DocumentCategory.OTHER,
        verbose_name=_('Category')
    )
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        verbose_name=_('File')
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents',
        verbose_name=_('Uploaded By')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Description / Notes')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Uploaded At')
    )

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def __str__(self):
        return f"{self.title} ({self.get_category_display()}) - {self.intern.user.get_full_name()}"

    @property
    def filename(self):
        import os
        return os.path.basename(self.file.name) if self.file else ''

    @property
    def extension(self):
        import os
        if not self.file:
            return ''
        ext = os.path.splitext(self.file.name)[1].lower()
        return ext.lstrip('.')
