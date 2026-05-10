from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from course_app.models import Course, CourseFeature, Lesson, DiscountCode, LessonPDF, Status
from course_app.api.serializer import CourseSerializer, CourseFeatureSerializer, LessonSerializer, PurchasedSerializer, DiscountCodeSerializer, LessonPDFSerializer, LessonSerializerCrm
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.utils import timezone
from invoice_app.models import PaymentStatus
from purchase_app.models import Purchase
from purchase_app.services import PurchaseService
from django.utils.translation import gettext_lazy as _
from customer_app.api.views import IsProfileComplete
from rest_framework.exceptions import ValidationError

# You can see all courses which you can buy
# Admin can create, update change the course


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

# You can see all features from course, belong to CourseViewSet


class CourseFeatureViewSet(viewsets.ModelViewSet):
    queryset = CourseFeature.objects.all()
    serializer_class = CourseFeatureSerializer
    permission_classes = [AllowAny]


class LessonViewSetCrmAPI(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializerCrm

    def get_queryset(self):
        course = self.request.query_params.get('course')
        if course:
            return Lesson.objects.filter(course=course)
        return Lesson.objects.all()


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]

    # Show all lessons which you bought
    def get_queryset(self):
        customer = self.request.user  # current logged user
        course_id = self.request.query_params.get('course')

        has_purchase = Purchase.objects.filter(
            customer=customer,
            course_id=course_id,
            status=PaymentStatus.PAID
        ).exists()

        if not has_purchase:
            raise PermissionDenied(
                {'message': _('We have not received your payment.')})

        return Lesson.objects.filter(
            course_id=course_id,
            status=Status.PUBLISHED
        )


# BUY BUY
# If you bought the course, you will see it
class PurchasedViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Purchase.objects.all()
    serializer_class = PurchasedSerializer
    permission_classes = [IsAuthenticated]

    # show you all courses which you bought with filter "lessons_count"
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(customer=self.request.user)
            .annotate(
                lessons_count=Count(
                    'course__lessons',
                    filter=Q(course__lessons__status=Status.PUBLISHED)
                )
            )
        )

    # With this method you can buy a course with bank transfer
    def perform_create(self, serializer):

        # class in purchase_app --> services.py
        service = PurchaseService()
        service.create_purchase(
            request=self.request,
            customer=self.request.user,
            course=serializer.validated_data['course'],
            discount=serializer.validated_data.get('discount'),
        )

#


class DiscountCodeViewSet(viewsets.ModelViewSet):
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_code(self, request):

        code = request.data.get('code')
        try:
            discount = DiscountCode.objects.get(code=code, active=True)
        except DiscountCode.DoesNotExist:
            return Response(
                {'detail': 'Invalid discount code.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # If the code has an expiration date AND that date is already in the past
        if discount.expires_at and discount.expires_at < timezone.now():
            return Response(
                {'detail': 'Discount code expired.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(discount)
        return Response(serializer.data)


class LessonPDFViewSet(viewsets.ModelViewSet):
    queryset = LessonPDF.objects.all()
    serializer_class = LessonPDFSerializer

