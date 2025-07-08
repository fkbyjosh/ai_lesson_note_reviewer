from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from django.contrib.auth import get_user_model
from .models import Teacher, LessonNote, Feedback
from .serializers import TeacherSerializer, LessonNoteSerializer, FeedbackSerializer, RegisterSerializer

User = get_user_model()

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return the teacher record for the current user
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            return Teacher.objects.filter(id=teacher.id)
        except Teacher.DoesNotExist:
            return Teacher.objects.none()

class LessonNoteViewSet(viewsets.ModelViewSet):
    serializer_class = LessonNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            return LessonNote.objects.filter(teacher=teacher)
        except Teacher.DoesNotExist:
            return LessonNote.objects.none()

    def perform_create(self, serializer):
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            serializer.save(teacher=teacher)
        except Teacher.DoesNotExist:
            pass

class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            return Feedback.objects.filter(lesson_note__teacher=teacher)
        except Teacher.DoesNotExist:
            return Feedback.objects.none()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully."}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)