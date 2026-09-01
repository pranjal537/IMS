"""
Tasks models for Damak Municipality IMS.
Phase 6: Task Management
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from interns.models import InternProfile, SupervisorProfile

class TaskPriority(models.TextChoices):
    LOW = 'LOW', _('Low')
    MEDIUM = 'MEDIUM', _('Medium')
    HIGH = 'HIGH', _('High')

class TaskStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    COMPLETED = 'COMPLETED', _('Completed')
    OVERDUE = 'OVERDUE', _('Overdue')

class Task(models.Model):
    title = models.CharField(_('task title'), max_length=255)
    description = models.TextField(_('description'))
    intern = models.ForeignKey(
        InternProfile,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('intern')
    )
    assigned_by = models.ForeignKey(
        SupervisorProfile,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        verbose_name=_('assigned by')
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING
    )
    start_date = models.DateField(_('start date'))
    due_date = models.DateField(_('due date'))
    progress = models.IntegerField(_('progress percentage'), default=0)
    supervisor_comment = models.TextField(_('supervisor comment'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.progress < 0 or self.progress > 100:
            raise ValidationError({'progress': _('Progress must be between 0 and 100.')})
        
        if self.start_date and self.due_date and self.due_date < self.start_date:
            raise ValidationError({'due_date': _('Due date cannot be before start date.')})

    def save(self, *args, **kwargs):
        # Synchronize progress and status
        if self.status == TaskStatus.COMPLETED:
            self.progress = 100
        elif self.progress == 100:
            self.status = TaskStatus.COMPLETED
            
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == TaskStatus.COMPLETED:
            return False
        if self.due_date < timezone.now().date():
            return True
        return False
    
    @property
    def display_status(self):
        if self.is_overdue:
            return TaskStatus.OVERDUE
        return self.status

    def get_status_badge_class(self):
        status_to_check = self.display_status
        mapping = {
            TaskStatus.PENDING: 'bg-secondary',
            TaskStatus.IN_PROGRESS: 'bg-primary',
            TaskStatus.COMPLETED: 'bg-success',
            TaskStatus.OVERDUE: 'bg-danger',
        }
        return mapping.get(status_to_check, 'bg-secondary')

    def get_priority_badge_class(self):
        mapping = {
            TaskPriority.LOW: 'bg-info text-dark',
            TaskPriority.MEDIUM: 'bg-warning text-dark',
            TaskPriority.HIGH: 'bg-danger',
        }
        return mapping.get(self.priority, 'bg-secondary')
