from rest_framework import serializers
from .models import Teacher, LessonNote, Feedback
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class TeacherSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'email', 'username', 'user_email']

class LessonNoteSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    teacher_id = serializers.CharField(source='teacher.id', read_only=True)
    feedback_count = serializers.SerializerMethodField()
    has_ai_feedback = serializers.SerializerMethodField()
    latest_feedback = serializers.SerializerMethodField()

    class Meta:
        model = LessonNote
        fields = [
            'id', 'subject', 'grade_level', 'term', 'content', 
            'submitted_at', 'status', 'teacher', 'teacher_name', 
            'teacher_id', 'feedback_count', 'has_ai_feedback', 
            'latest_feedback'
        ]
        read_only_fields = ['teacher', 'submitted_at']

    def get_feedback_count(self, obj):
        return obj.feedback_set.count()

    def get_has_ai_feedback(self, obj):
        return obj.feedback_set.filter(reviewer_type='AI').exists()

    def get_latest_feedback(self, obj):
        latest = obj.feedback_set.first()  # Uses ordering from model
        if latest:
            return {
                'id': latest.id,
                'reviewer': latest.reviewer,
                'reviewer_type': latest.reviewer_type,
                'score': latest.score,
                'created_at': latest.created_at,
                'overall_assessment': latest.overall_assessment
            }
        return None

class FeedbackSerializer(serializers.ModelSerializer):
    lesson_note_subject = serializers.CharField(source='lesson_note.subject', read_only=True)
    lesson_note_id = serializers.CharField(source='lesson_note.id', read_only=True)
    teacher_name = serializers.CharField(source='lesson_note.teacher.name', read_only=True)
    lesson_note_grade = serializers.CharField(source='lesson_note.grade_level', read_only=True)
    lesson_note_term = serializers.CharField(source='lesson_note.term', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'lesson_note', 'lesson_note_id', 'lesson_note_subject', 
            'lesson_note_grade', 'lesson_note_term', 'teacher_name',
            'reviewer', 'reviewer_type', 'feedback_text', 'score', 
            'strengths', 'suggestions', 'areas_for_improvement', 
            'overall_assessment', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_score(self, value):
        if value is not None and (value < 1 or value > 100):
            raise serializers.ValidationError("Score must be between 1 and 100")
        return value

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    username = serializers.CharField(
        required=True,
        help_text="Your full name for the teacher profile"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'username': {
                'validators': [UniqueValidator(queryset=User.objects.all())]
            }
        }

    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Create teacher profile automatically
        Teacher.objects.create(
            user=user,
            name=validated_data['username'],
            email=user.email
        )
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    teacher_id = serializers.CharField(source='teacher.id', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'teacher_name', 'teacher_id']
        read_only_fields = ['id', 'username']