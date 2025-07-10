from celery import shared_task
from .models import LessonNote, Feedback
from .ai_feedback import AIFeedbackGenerator

@shared_task
def generate_ai_feedback_async(lesson_note_id):
    """Generate AI feedback asynchronously"""
    try:
        lesson_note = LessonNote.objects.get(id=lesson_note_id)
        ai_generator = AIFeedbackGenerator()
        feedback_data = ai_generator.generate_feedback(lesson_note)
        
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
        print(f"Async AI feedback generation failed: {str(e)}")