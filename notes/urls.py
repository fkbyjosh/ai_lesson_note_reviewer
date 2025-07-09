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