from rest_framework.routers import DefaultRouter
from course_app.api import views
from django.urls import path

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet, basename='courses')
router.register(r'courses-features', views.CourseFeatureViewSet, basename='courses-features')
router.register(r'lessons', views.LessonViewSet, basename='lessons')
router.register(r'purchases', views.PurchasedViewSet, basename='purchases')
router.register(r'discount-codes', views.DiscountCodeViewSet, basename='discount-code')
# CRM part
router.register(r'crm-lessons', views.LessonViewSetCrmAPI, basename='crm-lessons')
router.register(r'crm-lesson-pdfs', views.LessonPDFViewSet, basename='crm-lesson-pdfs')

urlpatterns = [
    path(
        "lesson-progress/",
        views.LessonProgressAPIView.as_view(),
        name="lesson-progress"),

    path(
        "lesson-progress/<int:lesson_id>/",
        views.LessonProgressAPIView.as_view(),
        name="lesson-progress-detail"
    ),
]


urlpatterns += router.urls
