from rest_framework.viewsets import ModelViewSet
from .serializer import InvoiceSerializer, InvoiceServiceSerializer
from invoice_app.models import Invoice, InvoiceService
from customer_app.models import Customer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.template.response import TemplateResponse
from rest_framework.decorators import action
from django.shortcuts import render
from company_app.models import Company
from rest_framework import status

# You can onyl see the list of the invoices but you cannot change the invoice
class InvoiceView(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        services_data = data.pop("services", [])

        # 1. Validate and create the invoice (without snapshots)
        serializer = InvoiceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()

        # 2. CUSTOMER SNAPSHOT
        customer = invoice.customer
        invoice.customer_name = f"{customer.first_name} {customer.last_name}"
        invoice.customer_address = (
            f"{customer.street} {customer.number}, "
            f"{customer.postcode} {customer.city}"
        )

        # 3. COMPANY SNAPSHOT
        company = Company.objects.first()

        invoice.company_name = company.name
        invoice.company_street = company.street
        invoice.company_number = company.number
        invoice.company_postcode = company.postcode
        invoice.company_city = company.city
        invoice.company_tax_number = company.tax_number
        invoice.company_email = company.email
        invoice.company_bank = company.bank
        invoice.company_bank_account = company.bank_account
        invoice.company_swift_code = company.swift_code
        invoice.company_logo = company.logo

        invoice.save()

        # 4. CREATE INVOICE SERVICES
        for service in services_data:
            InvoiceService.objects.create(
            invoice=invoice,
            service_catalog=service.get("service_catalog"),
            custom_service_name=service.get("custom_service_name") or service.get("name"),
            amount=service.get("amount", 0),
        )
            
        if not invoice:
            return Response(
            {"error": "Invoice could not be created"},
            status=status.HTTP_400_BAD_REQUEST
            )       

        return Response(
            {"message": "Invoice created successfully", "invoice_id": invoice.id},
            status=status.HTTP_201_CREATED
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        invoice = self.get_object()

        new_status = request.data.get("payment_status")

        # Validate input
        valid_statuses = dict(Invoice.PaymentStatus.choices).keys()
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid payment_status. Allowed: {list(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status
        invoice.payment_status = new_status
        invoice.save()

        return Response(
            {"status": f"Payment status updated to: {new_status}"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def preview(self, request, pk=None):
        company = Company.objects.first()
        customer = Customer.objects.first()

        # invoice = self.get_object()
        return render(request, "invoice.html", {"company": company, 'customer': customer})

class InvoiceServiceView(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceServiceSerializer