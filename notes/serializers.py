from rest_framework import serializers
from .models import Teacher, LessonNote, Feedback
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class LessonNoteSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = LessonNote
        fields = '__all__'
        read_only_fields = ['teacher']

class FeedbackSerializer(serializers.ModelSerializer):
    lesson_note_subject = serializers.CharField(source='lesson_note.subject', read_only=True)
    lesson_note_title = serializers.CharField(source='lesson_note.title', read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'

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
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        user = User.objects.create_user(**validated_data)
        return user