from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from rest_framework.exceptions import ValidationError
from company_app.models import Company
from invoice_app.models import Invoice, InvoiceService, PriceType, Tax, PaymentStatus, PaymentMethod
from customer_app.api.views import IsProfileComplete
from auth_app.models import User
from invoice_app.invoice_number import GenerateInvoiceNumber
from weasyprint import HTML
from auth_app.models import User
from django.template.loader import render_to_string
from purchase_app.models import Purchase
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status


# For Bank Transfer
class PurchaseService:
    def create_purchase(self, request, customer, course, discount):

        net_price = course.price
        tax = Tax.objects.first()
        tax_percent = tax.percent

        discount_amount_value = 0
        net_price_after_discount = 0
        tax_amount = 0

        discount_percent = Decimal("0.00")
        discount_amount_value = Decimal("0.00")

        if discount:
            if not discount.active:
                raise ValueError('Discount code is not active.')

            discount_amount = (
                net_price * discount.percent_value / Decimal('100')
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            discount_amount_value = discount_amount
            discount_percent = discount.percent_value

            tax_amount_with_discount = (
                (net_price - discount_amount)  * tax_percent / Decimal('100')
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            tax_amount = tax_amount_with_discount
            
            net_price_after_discount = net_price - discount_amount + tax_amount
        else:
            tax_amount_without_discount = (
                net_price  * tax_percent / Decimal('100')
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
            tax_amount = tax_amount_without_discount

            net_price_after_discount = net_price + tax_amount_without_discount

        gross_price = (
            net_price_after_discount
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        company = Company.objects.first()

        # -------------------------
        # DATABASE TRANSACTION
        # -------------------------
        with transaction.atomic():

            purchase = Purchase.objects.create(
            customer=customer,
            course=course,
            discount=discount,
            status=PaymentStatus.UNPAID,
            subtotal=net_price,
            discount_percent=discount_percent,
            discount_amount=discount_amount_value,
            tax_percent=tax_percent,
            tax_amount=tax_amount,
            total=gross_price,
            payment_method=PaymentMethod.BANK_TRANSFER
        )

            business = User.objects.get(role=User.ProfileType.BUSINESS)

            invoice = Invoice.objects.create(
                business=business,
                customer=customer,
                invoice_number=GenerateInvoiceNumber.generate_invoice_number(),
                payment_method=PaymentMethod.BANK_TRANSFER,

                discount=discount_percent,
                discount_amount_value=discount_amount_value,

                amount=net_price,
                investitions_amount=gross_price,
                provision=0,
                value_tax=tax_percent,
                value_tax_amount=tax_amount,

                # --- CUSTOMER SNAPSHOT ---
                user_customer_id=customer.id,
                user_customer_number=customer.customer_number,
                user_customer_first_name=customer.first_name,
                user_customer_last_name=customer.last_name,
                user_customer_street=customer.street,
                user_customer_street_number=customer.street_number,
                user_customer_postcode=customer.postcode,
                user_customer_city=customer.city,

                # --- COMPANY SNAPSHOT ---
                company_name=company.name,
                company_street=company.street,
                company_street_number=company.street_number,
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
                provision_fixed=course.price,
                provision_amount=course.price
            )

            purchase.invoice = invoice
            purchase.save()

        # -------------------------
        # SEND EMAIL (outside transaction)
        # -------------------------
        if request:
            email_service = SendInvoiceEmail()
            email_service.send_invoice_email(request, invoice)

        return purchase

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


# This method check if the customer already bought a curse
# The customer can only once buy a curse.
class CheckPurchase:
    @staticmethod
    def check_purchase(customer, course_id):

        purchase = Purchase.objects.filter(
            customer=customer,
            course_id=course_id
        ).first()

        if purchase:
            return Response(
                {
                    'message': _('You already purchased this course.'),
                },
                 status=status.HTTP_409_CONFLICT
            )