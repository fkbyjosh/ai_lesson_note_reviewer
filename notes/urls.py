from rest_framework.routers import DefaultRouter
from .views import TeacherViewSet, LessonNoteViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'lesson-notes', LessonNoteViewSet)
router.register(r'feedback', FeedbackViewSet)

urlpatterns = router.urls