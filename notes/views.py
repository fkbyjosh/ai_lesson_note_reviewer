from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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
            lesson_note = LessonNote.objects.filter(teacher=teacher)
            return Feedback.objects.filter(lesson_note__in=lesson_note).order_by('-created_at')
        except Teacher.DoesNotExist:
            return LessonNote.objects.none()

    def perform_create(self, serializer):
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            lesson_note = serializer.save(teacher=teacher)
            
            # Generate AI feedback automatically after creating lesson note
            self.generate_ai_feedback(lesson_note)
            
        except Teacher.DoesNotExist:
            raise status.HTTP_400_BAD_REQUEST("Teacher profile not found")

    def generate_ai_feedback(self, lesson_note):
        """Generate AI feedback for a lesson note"""
        try:
            ai_generator = AIFeedbackGenerator()
            feedback_data = ai_generator.generate_feedback(lesson_note)
            
            # Create feedback record
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
            return feedback_data
        except Exception as e:
            # Log error in production
            print(f"Failed to generate AI feedback: {str(e)}")

 
    @action(detail=True, methods=['get'], url_path='feedback')
    def get_feedback(self, request, pk=None):
        """
        Get all feedback for a lesson note
        Endpoint: GET /api/lesson-notes/{id}/feedback/
        """
        print('what the helly')
        lesson_note = self.get_object()
        feedback = Feedback.objects.filter(lesson_note=lesson_note)
        serializer = FeedbackSerializer(feedback, many=True)
        return Response({
            'lesson_note_id': lesson_note.id,
            'feedback_count': feedback.count(),
            'feedback': serializer.data
        })

    @action(detail=True, methods=['delete'], url_path='ai-feedback')
    def delete_ai_feedback(self, request, pk=None):
        """
        Delete AI feedback for a lesson note (to regenerate)
        Endpoint: DELETE /api/lesson-notes/{id}/ai-feedback/
        """
        lesson_note = self.get_object()
        ai_feedback = Feedback.objects.filter(
            lesson_note=lesson_note, 
            reviewer_type='AI'
        )
        
        if ai_feedback.exists():
            count = ai_feedback.count()
            ai_feedback.delete()
            return Response({
                'message': f'Deleted {count} AI feedback record(s)',
                'lesson_note_id': lesson_note.id
            })
        else:
            return Response({
                'message': 'No AI feedback found to delete',
                'lesson_note_id': lesson_note.id
            }, status=status.HTTP_404_NOT_FOUND)

class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            return Feedback.objects.filter(lesson_note__teacher=teacher)
        except Teacher.DoesNotExist:
            return Feedback.objects.none()

    @action(detail=False, methods=['get'], url_path='ai-feedback')
    def get_all_ai_feedback(self, request):
        """
        Get all AI feedback for current teacher
        Endpoint: GET /api/feedback/ai-feedback/
        """
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            ai_feedback = Feedback.objects.filter(
                lesson_note__teacher=teacher,
                reviewer_type='AI'
            )
            serializer = FeedbackSerializer(ai_feedback, many=True)
            return Response({
                'count': ai_feedback.count(),
                'feedback': serializer.data
            })
        except Teacher.DoesNotExist:
            return Response({
                'error': 'Teacher profile not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='human-feedback')
    def get_all_human_feedback(self, request):
        """
        Get all human feedback for current teacher
        Endpoint: GET /api/feedback/human-feedback/
        """
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            human_feedback = Feedback.objects.filter(
                lesson_note__teacher=teacher,
                reviewer_type='HUMAN'
            )
            serializer = FeedbackSerializer(human_feedback, many=True)
            return Response({
                'count': human_feedback.count(),
                'feedback': serializer.data
            })
        except Teacher.DoesNotExist:
            return Response({
                'error': 'Teacher profile not found'
            }, status=status.HTTP_404_NOT_FOUND)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                "message": "User registered successfully.",
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher = Teacher.objects.get(user=request.user)
            return Response({
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "teacher_id": teacher.id,
                "teacher_name": teacher.name
            })
        except Teacher.DoesNotExist:
            return Response({
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "teacher_id": None,
                "teacher_name": None,
                "message": "Teacher profile not found"
            })

    def put(self, request):
        """Update user profile"""
        try:
            teacher = Teacher.objects.get(user=request.user)
            
            # Update user fields
            if 'email' in request.data:
                request.user.email = request.data['email']
                request.user.save()
            
            # Update teacher fields
            if 'name' in request.data:
                teacher.name = request.data['name']
            if 'email' in request.data:
                teacher.email = request.data['email']
            teacher.save()
            
            return Response({
                "message": "Profile updated successfully",
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "teacher_id": teacher.id,
                "teacher_name": teacher.name
            })
        except Teacher.DoesNotExist:
            return Response({
                "error": "Teacher profile not found"
            }, status=status.HTTP_404_NOT_FOUND)