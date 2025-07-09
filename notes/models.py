from django.db import models
from django.conf import settings
import json

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class LessonNote(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    grade_level = models.CharField(max_length=20)
    term = models.CharField(max_length=10)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.subject} - {self.teacher.name}"

class Feedback(models.Model):
    REVIEWER_TYPES = [
        ('AI', 'AI Generated'),
        ('HUMAN', 'Human Reviewer'),
    ]
    
    lesson_note = models.ForeignKey(LessonNote, on_delete=models.CASCADE)
    reviewer = models.CharField(max_length=100)
    reviewer_type = models.CharField(max_length=10, choices=REVIEWER_TYPES, default='AI')
    feedback_text = models.TextField()
    score = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    #additional AI feedback fields
    strengths = models.JSONField(default=list, blank=True)
    suggestions = models.JSONField(default=list, blank=True)
    areas_for_improvement = models.JSONField(default=list, blank=True)
    overall_assessment = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer_type} Feedback for {self.lesson_note}"