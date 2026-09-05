from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from interns.models import Internship

class RecommendationChoices(models.TextChoices):
    HIGHLY_RECOMMENDED = 'HIGHLY_RECOMMENDED', _('Highly Recommended')
    RECOMMENDED = 'RECOMMENDED', _('Recommended')
    RECOMMENDED_WITH_IMPROVEMENT = 'RECOMMENDED_WITH_IMPROVEMENT', _('Recommended with Improvement')
    NOT_RECOMMENDED = 'NOT_RECOMMENDED', _('Not Recommended')

class Evaluation(models.Model):
    internship = models.OneToOneField(
        Internship, 
        on_delete=models.CASCADE, 
        related_name='evaluation'
    )
    
    # Ratings (1-5)
    technical_skills = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    problem_solving = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    professionalism = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    work_quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    learning_ability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    discipline = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Comments
    strengths = models.TextField(blank=True)
    improvement_areas = models.TextField(blank=True)
    overall_comments = models.TextField(blank=True)
    
    # Conclusion
    final_recommendation = models.CharField(
        max_length=50,
        choices=RecommendationChoices.choices
    )
    overall_score = models.FloatField(editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('evaluation')
        verbose_name_plural = _('evaluations')
        ordering = ['-created_at']

    def __str__(self):
        return f"Evaluation for {self.internship.intern.user.get_full_name()}"

    def calculate_score(self):
        fields = [
            self.technical_skills, self.communication, self.punctuality,
            self.problem_solving, self.professionalism, self.work_quality,
            self.learning_ability, self.discipline
        ]
        # filter out None values just in case during validation before saving
        valid_fields = [f for f in fields if f is not None]
        if not valid_fields:
            return 0.0
        return round(sum(valid_fields) / len(valid_fields), 2)

    def clean(self):
        super().clean()
        fields = [
            ('technical_skills', self.technical_skills),
            ('communication', self.communication),
            ('punctuality', self.punctuality),
            ('problem_solving', self.problem_solving),
            ('professionalism', self.professionalism),
            ('work_quality', self.work_quality),
            ('learning_ability', self.learning_ability),
            ('discipline', self.discipline),
        ]
        errors = {}
        for name, value in fields:
            if value is not None and (value < 1 or value > 5):
                errors[name] = _('Rating must be between 1 and 5.')
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.overall_score = self.calculate_score()
        self.full_clean()
        super().save(*args, **kwargs)
