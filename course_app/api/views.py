from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from course_app.models import Course, CourseFeature, Lesson, Purchase, DiscountCode
from course_app.api.serializer import CourseSerializer, CourseFeatureSerializer, LessonSerializer, PurchasedSerializer, DiscountCodeSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from decimal import Decimal
from django.db.models import Count
from django.utils import timezone
from decimal import ROUND_HALF_UP
from django.db import transaction
from company_app.models import Company
from invoice_app.models import Invoice, InvoiceService, PriceType
from invoice_app.invoice_number import GenerateInvoiceNumber
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from auth_app.models import User

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

    def get_queryset(self):
        customer = self.request.user
        course_id = self.request.query_params.get('course')

        has_purchase = Purchase.objects.filter(
            customer=customer,
            course_id=course_id
        ).exists()

        if not has_purchase:
            raise PermissionDenied('You did not purchase this course.')

        return Lesson.objects.filter(
            course_id=course_id,
        ).order_by("order")


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

    # with this method you can buy a course
    def perform_create(self, serializer):
        customer = self.request.user
        course = serializer.validated_data['course']
        discount = serializer.validated_data.get('discount')

        if Purchase.objects.filter(customer=customer, course=course).exists():
            raise ValidationError('You already purchased this course.')

        price = course.price

        if discount:
            if not discount.active:
                raise ValueError('Discount code is not active.')
            price = price * (Decimal('100') -
                             discount.percent_value) / Decimal('100')

        price = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        company = Company.objects.first()

        with transaction.atomic():
            # Purchase save
            purchase = serializer.save(
                customer=customer,
                price=price
            )

            business = User.objects.get(type=User.ProfileType.BUSINESS)

            invoice = Invoice.objects.create(
                business=business,
                customer=customer,
                invoice_number=GenerateInvoiceNumber.generate_invoice_number(),

                amount=price,
                investitions_amount=price,
                provision=0,
                value_tax=0,

                # --- CUSTOMER SNAPSHOT ---
                user_customer_id=customer.id,
                user_customer_number=customer.customer_number,
                user_customer_first_name=customer.first_name,
                user_customer_last_name=customer.last_name,
                user_customer_street=customer.street,
                user_customer_street_number=customer.number,
                user_customer_postcode=customer.postcode,
                user_customer_city=customer.city,

                # --- COMPANY SNAPSHOT ---
                company_name=company.name,
                company_street=company.street,
                company_number=company.number,
                company_postcode=company.postcode,
                company_city=company.city,
                company_tax_number=company.tax_number,
                company_email=company.email,
                company_bank=company.bank,
                company_bank_account=company.bank_account,
                company_swift_code=company.swift_code,
                company_logo=company.logo,
            )

            InvoiceService.objects.create(
                invoice=invoice,
                service_name=course.name,
                provision_type=PriceType.FIXED,
                provision_fixed=price,
                provision_amount=price
            )

            # Verbindung
            # invoice id
            purchase.invoice = invoice
            purchase.save()

    @action(detail=True, methods=['get'])
    def create_pdf(self, request, pk=None):
        purchase = self.get_object()
        invoice = purchase.invoice

        pdf_service = CreateInvoicePDF()
        return pdf_service.create_invoice(request, invoice)


class DiscountCodeViewSet(viewsets.ModelViewSet):
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAdminUser]

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

        return Response(
            {
                "code": discount.code,
                "percent_value": discount.percent_value,
                "valid": True
            }
        )


class CreateCourseInvoice:
    def creat_course_invoice():
        pass

# Create and download the invoice as PDF
class CreateInvoicePDF:
    def create_invoice(self, request, invoice):
        html_string = render_to_string('templates/invoice_course.html', {
            "invoice": invoice
        })

        # weasyprint
        html = HTML(
            string=html_string,
            base_url=request.build_absolute_uri()
        )

        # write_pdf belong to weasyprint
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="invoice_{invoice.id}_{invoice.invoice_number}.pdf"'
        )

        return response
