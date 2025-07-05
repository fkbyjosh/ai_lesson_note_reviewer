from django.shortcuts import render

from rest_framework import viewsets
from .models import Teacher, LessonNote, Feedback
from .serializers import TeacherSerializer, LessonNoteSerializer, FeedbackSerializer

class TeacherViewSet(viewsets.ModelViewSet):
  queryset = Teacher.objects.all()
  serializer_class = TeacherSerializer

class LessonNoteViewSet(viewsets.ModelViewSet):
  queryset = LessonNote.objects.all()
  serializer_class = LessonNoteSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
  queryset = Feedback.objects.all()
  serializer_class = FeedbackSerializer