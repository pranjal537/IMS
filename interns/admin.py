from django.contrib import admin
from .models import Department, SupervisorProfile, InternProfile, Internship


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'position', 'phone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id', 'position')
    list_filter = ('department',)
    ordering = ('employee_id',)


@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    list_display = ('intern_id', 'user', 'college', 'program', 'semester_or_year', 'phone')
    search_fields = ('intern_id', 'user__email', 'user__first_name', 'user__last_name', 'college', 'program')
    ordering = ('intern_id',)


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('intern', 'supervisor', 'department', 'position', 'start_date', 'expected_end_date', 'status')
    search_fields = ('intern__intern_id', 'intern__user__first_name', 'intern__user__last_name', 'supervisor__user__first_name', 'supervisor__user__last_name', 'position')
    list_filter = ('status', 'department', 'start_date')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)
