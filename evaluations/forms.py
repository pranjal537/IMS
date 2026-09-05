from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Evaluation, RecommendationChoices

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = [
            'technical_skills', 'communication', 'punctuality', 
            'problem_solving', 'professionalism', 'work_quality', 
            'learning_ability', 'discipline', 
            'strengths', 'improvement_areas', 'overall_comments', 
            'final_recommendation'
        ]
        
        widgets = {
            'technical_skills': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'communication': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'punctuality': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'problem_solving': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'professionalism': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'work_quality': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'learning_ability': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'discipline': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'improvement_areas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'overall_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            'final_recommendation': forms.Select(attrs={'class': 'form-select'}),
        }
