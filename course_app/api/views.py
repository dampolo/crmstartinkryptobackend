from rest_framework import status
from rest_framework import viewsets
from course_app.models import Course, CourseFeature, Lesson, Purchase
from course_app.api.serializer import CourseSerializer, CourseFeatureSerializer, LessonSerializer, PurchaseSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from decimal import Decimal
from django.db.models import Count
from decimal import ROUND_HALF_UP

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

class CourseFeatureViewSet(viewsets.ModelViewSet):
    queryset = CourseFeature.objects.all()
    serializer_class = CourseFeatureSerializer
    permission_classes = [AllowAny]

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request)
        user = self.request.user
        course_id = self.request.query_params.get('course')

        has_purchase = Purchase.objects.filter(
            user=user,
            course_id=course_id
        ).exists()

        if not has_purchase:
            raise PermissionDenied('You did not purchase this course.')

        return Lesson.objects.filter(
            course_id=course_id,
        ).order_by("order")

class PurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
                Purchase.objects
                .filter(user=self.request.user)
                .annotate(lessons_count=Count('course__lessons'))
        )

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data['course']
        discount = serializer.validated_data.get('discount')

        if Purchase.objects.filter(user=user, course=course).exists():
            raise ValidationError('You already purchased this course.')
        
        price = course.price

        if discount:
            if not discount.active:
                raise ValueError('Discount code is not active.')
            price = price * (Decimal('100') - discount.percent_value) / Decimal('100')

        price = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        serializer.save(
            user=user,
            price=price
        )