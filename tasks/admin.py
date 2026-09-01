from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'intern', 'assigned_by', 'priority', 'status', 'progress', 'due_date')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'intern__user__first_name', 'intern__user__last_name', 'intern__intern_id')
    readonly_fields = ('created_at', 'updated_at')
