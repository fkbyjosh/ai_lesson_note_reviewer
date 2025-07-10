from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import json

class Teacher(models.Model):
    """Teacher model linked to Django User"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Sync email with user email if not provided
        if not self.email and self.user.email:
            self.email = self.user.email
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

class LessonNote(models.Model):
    """Lesson note model for storing teacher submissions"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='lesson_notes')
    subject = models.CharField(max_length=100)
    grade_level = models.CharField(max_length=20)
    term = models.CharField(max_length=10)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.subject} - {self.grade_level} - {self.teacher.name}"

    @property
    def feedback_count(self):
        """Get total feedback count"""
        return self.feedback_set.count()

    @property
    def has_ai_feedback(self):
        """Check if lesson note has AI feedback"""
        return self.feedback_set.filter(reviewer_type='AI').exists()

    @property
    def latest_feedback(self):
        """Get latest feedback"""
        return self.feedback_set.first()

    @property
    def ai_feedback(self):
        """Get AI feedback if exists"""
        return self.feedback_set.filter(reviewer_type='AI').first()

    class Meta:
        verbose_name = "Lesson Note"
        verbose_name_plural = "Lesson Notes"
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['teacher', 'subject']),
            models.Index(fields=['status']),
            models.Index(fields=['submitted_at']),
        ]

class Feedback(models.Model):
    """Feedback model for both AI and human reviews"""
    REVIEWER_TYPES = [
        ('AI', 'AI Generated'),
        ('HUMAN', 'Human Reviewer'),
    ]
    
    lesson_note = models.ForeignKey(LessonNote, on_delete=models.CASCADE, related_name='feedback_set')
    reviewer = models.CharField(max_length=100)
    reviewer_type = models.CharField(max_length=10, choices=REVIEWER_TYPES, default='AI')
    feedback_text = models.TextField()
    score = models.IntegerField(blank=True, null=True, help_text="Score from 1-100")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional AI feedback fields - structured data
    strengths = models.JSONField(default=list, blank=True, help_text="List of strengths identified")
    suggestions = models.JSONField(default=list, blank=True, help_text="List of suggestions for improvement")
    areas_for_improvement = models.JSONField(default=list, blank=True, help_text="List of areas needing improvement")
    overall_assessment = models.TextField(blank=True, help_text="Overall assessment summary")
    
    def __str__(self):
        return f"{self.reviewer_type} Feedback for {self.lesson_note.subject} by {self.lesson_note.teacher.name}"

    def clean(self):
        """Validate model data"""
        from django.core.exceptions import ValidationError
        
        # Validate score range
        if self.score is not None and (self.score < 1 or self.score > 100):
            raise ValidationError({'score': 'Score must be between 1 and 100'})
        
        # Ensure JSON fields are lists
        if not isinstance(self.strengths, list):
            self.strengths = []
        if not isinstance(self.suggestions, list):
            self.suggestions = []
        if not isinstance(self.areas_for_improvement, list):
            self.areas_for_improvement = []

    def save(self, *args, **kwargs):
        """Override save to run clean validation"""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_ai_generated(self):
        """Check if feedback is AI generated"""
        return self.reviewer_type == 'AI'

    @property
    def is_human_review(self):
        """Check if feedback is human review"""
        return self.reviewer_type == 'HUMAN'

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lesson_note', 'reviewer_type']),
            models.Index(fields=['reviewer_type']),
            models.Index(fields=['created_at']),
        ]

    # Additional methods for better data handling
    def get_strengths_display(self):
        """Get strengths as formatted string"""
        if self.strengths:
            return "; ".join(self.strengths)
        return "None specified"

    def get_suggestions_display(self):
        """Get suggestions as formatted string"""
        if self.suggestions:
            return "; ".join(self.suggestions)
        return "None specified"

    def get_areas_for_improvement_display(self):
        """Get areas for improvement as formatted string"""
        if self.areas_for_improvement:
            return "; ".join(self.areas_for_improvement)
        return "None specified"