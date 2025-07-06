from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import TeacherViewSet, LessonNoteViewSet, FeedbackViewSet
from .views import RegisterView

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teachers')
router.register(r'lesson-notes', LessonNoteViewSet, basename='lesson-notes')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

urlpatterns = [
	path('register/', RegisterView.as_view(), name='register'),
] + router.urls