from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('intern', 'date', 'status', 'check_in', 'check_out', 'created_at')
    list_filter = ('status', 'date', 'intern__internship__department')
    search_fields = ('intern__intern_id', 'intern__user__first_name', 'intern__user__last_name', 'remarks')
    date_hierarchy = 'date'
    ordering = ('-date', '-check_in')
