from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from django.contrib.auth import get_user_model
from .models import Teacher, LessonNote, Feedback
from .serializers import TeacherSerializer, LessonNoteSerializer, FeedbackSerializer, RegisterSerializer

class TeacherViewSet(viewsets.ModelViewSet):
  queryset = Teacher.objects.all()
  serializer_class = TeacherSerializer

class LessonNoteViewSet(viewsets.ModelViewSet):
  serializer_class = LessonNoteSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    return LessonNote.objects.filter(teacher__user=self.request.user)

class FeedbackViewSet(viewsets.ModelViewSet):
  queryset = Feedback.objects.all()
  serializer_class = FeedbackSerializer

User = get_user_model()

class RegisterView(APIView):
  def post(self, request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)