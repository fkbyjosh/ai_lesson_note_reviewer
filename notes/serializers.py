from rest_framework import serializers
from .models import Teacher, LessonNote, Feedback

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class LessonNoteSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = LessonNote
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    lesson_note_subject = serializers.CharField(source='lesson_note.subject', read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'
