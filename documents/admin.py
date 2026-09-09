from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'intern', 'category', 'uploaded_by', 'uploaded_at')
    list_filter = ('category', 'uploaded_at')
    search_fields = (
        'title',
        'intern__user__first_name',
        'intern__user__last_name',
        'intern__user__email',
        'intern__intern_id'
    )
    raw_id_fields = ('intern', 'uploaded_by')
    date_hierarchy = 'uploaded_at'
