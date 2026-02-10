from rest_framework.routers import DefaultRouter
from course_app.api.views import CourseViewSet, CourseFeatureViewSet, LessonViewSet, PurchaseViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'courses-features', CourseFeatureViewSet, basename='courses-features')
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"purchases", PurchaseViewSet, basename="purchase")

urlpatterns = router.urls
