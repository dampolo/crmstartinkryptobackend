from rest_framework.routers import DefaultRouter
from course_app.api.views import CourseViewSet, CourseFeatureViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'courses-features', CourseFeatureViewSet, basename='courses-features')


urlpatterns = router.urls
