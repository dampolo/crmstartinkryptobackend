from rest_framework.routers import DefaultRouter
from course_app.api.views import CourseViewSet, CourseFeatureViewSet, LessonViewSet, PurchasedViewSet, DiscountCodeViewSet, LessonPDFSerializer
from course_app.api import views

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'courses-features', CourseFeatureViewSet, basename='courses-features')
router.register(r'lessons', LessonViewSet, basename='lessons')
router.register(r'purchases', PurchasedViewSet, basename='purchases')
router.register(r'discount-codes', DiscountCodeViewSet, basename='discount-code')
# router.register(r'lesson-pdfs', LessonViewSet, basename='lesson-pdfs')

# CRM part
router.register(r'crm-lessons', views.LessonViewSetCrmAPI, basename='crm-lessons')
router.register(r'crm-lesson-pdfs', views.LessonPDFViewSet, basename='crm-lesson-pdfs')



urlpatterns = router.urls
