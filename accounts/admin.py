from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the custom User model.
    Allows viewing, adding, editing, searching, and filtering users.
    """

    # List view columns
    list_display = ('email', 'get_full_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_display_links = ('email', 'get_full_name')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    list_editable = ('is_active',)
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    date_hierarchy = 'date_joined'

    # Detail view fieldsets
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name')
        }),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Add user form fieldsets
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name',
                'role', 'password1', 'password2',
                'is_active', 'is_staff',
            ),
        }),
    )

    readonly_fields = ('date_joined', 'last_login')

    # The default UserAdmin expects 'username' — override for email-based model
    filter_horizontal = ('groups', 'user_permissions')
