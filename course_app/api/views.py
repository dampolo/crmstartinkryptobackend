from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from course_app.models import Course, CourseFeature, Lesson, DiscountCode
from course_app.api.serializer import CourseSerializer, CourseFeatureSerializer, LessonSerializer, PurchasedSerializer, DiscountCodeSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from decimal import Decimal
from django.db.models import Count
from django.utils import timezone
from decimal import ROUND_HALF_UP
from django.db import transaction
from company_app.models import Company
from invoice_app.models import Invoice, InvoiceService, PriceType, Tax
from invoice_app.invoice_number import GenerateInvoiceNumber
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from auth_app.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from purchase_app.models import Purchase
from purchase_app.services import PurchaseService

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


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]

    # Show all lessons which you bought
    def get_queryset(self):
        customer = self.request.user  # current logged user
        course_id = self.request.query_params.get('course')

        has_purchase = Purchase.objects.filter(
            customer=customer,
            course_id=course_id
        ).exists()

        if not has_purchase:
            raise PermissionDenied('You did not purchase this course.')

        return Lesson.objects.filter(
            course_id=course_id,
        )


# BUY BUY
# If you bought the course, you will see it
class PurchasedViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchasedSerializer
    permission_classes = [IsAuthenticated]

    # show you all courses which you bought
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(customer=self.request.user)
            .annotate(lessons_count=Count('course__lessons'))
        )

    # With this method you can buy a course
    def perform_create(self, serializer):
        service = PurchaseService()
        service.create_purchase(
            customer=self.request.user,
            course=serializer.validated_data['course'],
            discount=serializer.validated_data.get('discount'),
            request=self.request
        )

#

class DiscountCodeViewSet(viewsets.ModelViewSet):
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def validate_code(self, request):

        code = request.data.get("code")
        try:
            discount = DiscountCode.objects.get(code=code, active=True)
        except DiscountCode.DoesNotExist:
            return Response(
                {"detail": "Invalid discount code."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # If the code has an expiration date AND that date is already in the past
        if discount.expires_at and discount.expires_at < timezone.now():
            return Response(
                {"detail": "Discount code expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(discount)
        return Response(serializer.data)



