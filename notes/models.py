from django.db import models
from django.conf import settings

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
    lesson_note = models.ForeignKey(LessonNote, on_delete=models.CASCADE)
    reviewer = models.CharField(max_length=100)  # could be AI or human with higher authorization
    feedback_text = models.TextField()
    score = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.lesson_note}"