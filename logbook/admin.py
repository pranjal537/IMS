from django.contrib import admin
from .models import DailyLog, DailyLogStatus


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for DailyLog.
    Supports search by intern and title, filter by status and date.
    """
    list_display = (
        'intern_name', 'date', 'title_short', 'hours_worked',
        'status_badge', 'has_feedback', 'created_at'
    )
    list_filter = ('status', 'date', 'intern__internship__department')
    search_fields = (
        'intern__user__first_name', 'intern__user__last_name',
        'intern__intern_id', 'title', 'description'
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date', '-created_at')
    list_per_page = 25

    fieldsets = (
        ('Log Entry', {
            'fields': ('intern', 'date', 'title', 'description', 'skills_learned', 'challenges', 'hours_worked')
        }),
        ('Review', {
            'fields': ('status', 'supervisor_feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def intern_name(self, obj):
        return obj.intern.user.get_full_name()
    intern_name.short_description = 'Intern'
    intern_name.admin_order_field = 'intern__user__first_name'

    def title_short(self, obj):
        return obj.title[:60] + ('…' if len(obj.title) > 60 else '')
    title_short.short_description = 'Activity Title'

    def status_badge(self, obj):
        colors = {
            DailyLogStatus.PENDING: '#ffc107',
            DailyLogStatus.APPROVED: '#198754',
            DailyLogStatus.REJECTED: '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return f'<span style="color:{color};font-weight:600;">{obj.get_status_display()}</span>'
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True

    def has_feedback(self, obj):
        return bool(obj.supervisor_feedback)
    has_feedback.short_description = 'Feedback?'
    has_feedback.boolean = True
