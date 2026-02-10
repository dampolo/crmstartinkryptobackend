from rest_framework import status
from rest_framework import viewsets
from course_app.models import Course, CourseFeature
from course_app.api.serializer import CourseSerializer, CourseFeatureSerializer
from rest_framework.permissions import AllowAny

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

class CourseFeatureViewSet(viewsets.ModelViewSet):
    queryset = CourseFeature.objects.all()
    serializer_class = CourseFeatureSerializer
    permission_classes = [AllowAny]

