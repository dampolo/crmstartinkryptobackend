from rest_framework.decorators import api_view
from rest_framework.response import Response
from paypal_app.utilis import create_paypal_order, capture_paypal_order, calculate_course_price
from django.db import transaction
from auth_app.models import User
from invoice_app.models import Invoice, InvoiceService, PriceType
from invoice_app.invoice_number import GenerateInvoiceNumber
from company_app.models import Company
from rest_framework import views
from purchase_app.models import Purchase
from decimal import Decimal
from rest_framework import status
from django.db import transaction
from purchase_app.services import SendInvoiceEmail

class CreateOrderView(views.APIView):
    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        discount_id = request.data.get("discount")
        customer = request.user

        pricing = calculate_course_price(course_id, discount_id, customer)
        print('#############################')
        print(pricing)
        purchase = Purchase.objects.create(
            customer=customer,
            course=pricing["course"],
            discount=pricing["discount"],
            status=Purchase.StatusChoices.OPEN,
            subtotal=pricing["subtotal"],
            discount_percent=pricing["discount_percent"],
            discount_amount=pricing["discount_amount"],
            tax_percent=pricing["tax_percent"],
            tax_amount=pricing["tax_amount"],
            total=pricing["total"],
        )

        paypal_order = create_paypal_order(pricing["total"])

        purchase.paypal_order_id = paypal_order["id"]
        purchase.save(update_fields=["paypal_order_id"])

        return Response({
            "orderID": paypal_order["id"]
        })

class CaptureOrderView(views.APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        order_id = request.data.get("orderID")

        if not order_id:
            return Response(
                {"error": "Missing orderID"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1 Get purchase
        try:
            purchase = Purchase.objects.select_for_update().get(
                paypal_order_id=order_id
            )
        except Purchase.DoesNotExist:
            return Response(
                {"error": "Purchase not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2 Idempotency check
        if purchase.status == Purchase.StatusChoices.PAID:
            return Response({"message": "Already captured"})

        # 3 Capture PayPal
        capture_data = capture_paypal_order(order_id)

        capture_status = capture_data["status"]

        if capture_status != "COMPLETED":
            purchase.status = Purchase.StatusChoices.FAILED
            purchase.save(update_fields=["status"])
            return Response(
                {"error": "Payment not completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4 Verify amount
        paid_amount = Decimal(
            capture_data["purchase_units"][0]["payments"]
            ["captures"][0]["amount"]["value"]
        )

        if paid_amount != purchase.total:
            return Response(
                {"error": "Amount mismatch"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5 Mark as paid
        purchase.status = Purchase.StatusChoices.PAID
        purchase.save(update_fields=["status"])

        company = Company.objects.first()

        business = User.objects.get(type=User.ProfileType.BUSINESS)
        # 6 Create invoice
        invoice = Invoice.objects.create(
            business=business,
            customer=purchase.customer,
            invoice_number=GenerateInvoiceNumber.generate_invoice_number(),

            discount=purchase.percent_value if purchase.discount_amount else 0,
            discount_amount_value=purchase.discount_amount,

            amount=purchase.subtotal,
            investitions_amount=purchase.total,
            provision=0,
            value_tax=purchase.tax_percent,
            value_tax_amount=purchase.tax_amount,

            # --- CUSTOMER SNAPSHOT ---
            user_customer_id=purchase.customer.id,
            user_customer_number=purchase.customer.customer_number,
            user_customer_first_name=purchase.customer.first_name,
            user_customer_last_name=purchase.customer.last_name,
            user_customer_street=purchase.customer.street,
            user_customer_street_number=purchase.customer.street_number,
            user_customer_postcode=purchase.customer.postcode,
            user_customer_city=purchase.customer.city,

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
            service_name=purchase.course.name,
            provision_type=PriceType.FIXED,
            provision_fixed=purchase.course.price,
            provision_amount=purchase.course.price
        )

        purchase.invoice = invoice
        purchase.save()

        email_service = SendInvoiceEmail()
        email_service.send_invoice_email(request, invoice)
        
        return Response({
            "status": "success",
            "invoice_id": invoice.id
        })
