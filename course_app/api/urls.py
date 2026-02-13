from rest_framework.routers import DefaultRouter
from course_app.api.views import CourseViewSet, CourseFeatureViewSet, LessonViewSet, PurchasedViewSet, DiscountCodeViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'courses-features', CourseFeatureViewSet, basename='courses-features')
router.register(r"lessons", LessonViewSet, basename="lessons")
router.register(r"purchases", PurchasedViewSet, basename="purchases")
router.register(r"discount-codes", DiscountCodeViewSet, basename="discount-code")

urlpatterns = router.urls
