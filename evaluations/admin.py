from django.contrib import admin
from .models import Evaluation

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('internship', 'overall_score', 'final_recommendation', 'created_at')
    list_filter = ('final_recommendation',)
    search_fields = ('internship__intern__user__first_name', 'internship__intern__user__last_name', 'internship__intern__intern_id')
    readonly_fields = ('overall_score', 'created_at', 'updated_at')
