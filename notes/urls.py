from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    TeacherViewSet,
    LessonNoteViewSet,
    FeedbackViewSet,
    RegisterView,
    ProfileView,
)

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teachers')
router.register(r'lesson-notes', LessonNoteViewSet, basename='lesson-notes')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
] + router.urls

# This will generate the following URL patterns:
# /api/register/ - POST (register new user) - done
# /api/profile/ - GET, PUT (get/update profile)
# /api/teachers/ - GET, POST (list/create teachers)
# /api/teachers/{id}/ - GET, PUT, DELETE (teacher details)
# /api/lesson-notes/ - GET, POST (list/create lesson notes)
# /api/lesson-notes/{id}/ - GET, PUT, DELETE (lesson note details)
# /api/lesson-notes/{id}/generate-ai-feedback/ - POST (generate AI feedback)
# /api/lesson-notes/{id}/ai-feedback/ - GET, DELETE (get/delete AI feedback)
# /api/lesson-notes/{id}/feedback/ - GET (get all feedback)
# /api/feedback/ - GET, POST (list/create feedback)
# /api/feedback/{id}/ - GET, PUT, DELETE (feedback details)
# /api/feedback/ai-feedback/ - GET (get all AI feedback for teacher)
# /api/feedback/human-feedback/ - GET (get all human feedback for teacher)