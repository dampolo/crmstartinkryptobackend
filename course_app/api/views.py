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
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

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
        customer = self.request.user #current logged user
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
        customer = self.request.user
        course = serializer.validated_data['course']
        discount = serializer.validated_data.get('discount')

        if Purchase.objects.filter(customer=customer, course=course).exists():
            raise ValidationError({
                'message': 'Du hast schon den Kurs gekauft.'
            })

        price = course.price

        if discount:
            if not discount.active:
                raise ValueError('Discount code is not active.')
            price = price * (Decimal('100') -
                             discount.percent_value) / Decimal('100')

        price = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        company = Company.objects.first()

        # Creat invoice
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

        # Send Invoice via E-Mail
        email_service = SendInvoiceEmail()
        email_service.send_invoice_email(self.request, invoice)

# 
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

# Create only Invoice in PDF
class CreateInvoicePDF:
    def create_pdf(self, request, invoice):
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

        # Only Invoice in PDF
        return pdf

# After purchase will send you the E-Mail with invoice
class SendInvoiceEmail:
    def send_invoice_email(self, request, invoice):
        from django.core.mail import EmailMessage
        from django.conf import settings

        customer = invoice.customer

        pdf_service = CreateInvoicePDF()
        pdf_file = pdf_service.create_pdf(request, invoice)

        # Build email
        body = {
            "first_name": customer.first_name,
        }

        html_answer = render_to_string(
            "templates/email_with_invoice.html", body)
        confirmation_message = EmailMessage(
            subject=f"Deine Rechnung {invoice.invoice_number}",
            body=html_answer,
            from_email=f"Start in Krypto <{settings.DEFAULT_FROM_EMAIL}>",
            to=[customer.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )

        confirmation_message.attach(
            f"invoice_{invoice.invoice_number}.pdf",
            pdf_file,
            "application/pdf"
        )

        confirmation_message.content_subtype = "html"
        confirmation_message.send()
