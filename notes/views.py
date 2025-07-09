from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from django.contrib.auth import get_user_model
from .models import Teacher, LessonNote, Feedback
from .serializers import TeacherSerializer, LessonNoteSerializer, FeedbackSerializer, RegisterSerializer
from rest_framework.decorators import action
from django.utils import timezone
from .ai_feedback import AIFeedbackGenerator

User = get_user_model()

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        #only return the teacher record for the current user
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
            lesson_note = serializer.save(teacher=teacher)
            
            #generate AI feedback asynchronously (recommended for production)
            self.generate_ai_feedback(lesson_note)
            
        except Teacher.DoesNotExist:
            pass

    def generate_ai_feedback(self, lesson_note):
        """Generate AI feedback for a lesson note"""
        try:
            ai_generator = AIFeedbackGenerator()
            feedback_data = ai_generator.generate_feedback(lesson_note)
            
            #create feedback record
            Feedback.objects.create(
                lesson_note=lesson_note,
                reviewer='AI Assistant',
                reviewer_type='AI',
                feedback_text=feedback_data['feedback_text'],
                score=feedback_data['score'],
                strengths=feedback_data['strengths'],
                suggestions=feedback_data['suggestions'],
                areas_for_improvement=feedback_data['areas_for_improvement'],
                overall_assessment=feedback_data['overall_assessment']
            )
            
        except Exception as e:
            #log error in production
            print(f"Failed to generate AI feedback: {str(e)}")

    @action(detail=True, methods=['post'])
    def request_ai_feedback(self, request, pk=None):
        """Manually request AI feedback for a lesson note"""
        lesson_note = self.get_object()
        
        #check if AI feedback already exists
        existing_feedback = Feedback.objects.filter(
            lesson_note=lesson_note, 
            reviewer_type='AI'
        ).first()
        
        if existing_feedback:
            return Response({
                'message': 'AI feedback already exists for this lesson note',
                'feedback_id': existing_feedback.id
            })
        
        #generate new AI feedback
        self.generate_ai_feedback(lesson_note)
        
        return Response({
            'message': 'AI feedback generated successfully',
            'lesson_note_id': lesson_note.id
        })

    @action(detail=True, methods=['get'])
    def feedback(self, request, pk=None):
        """Get all feedback for a lesson note"""
        lesson_note = self.get_object()
        feedback = Feedback.objects.filter(lesson_note=lesson_note)
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data)

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
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        })