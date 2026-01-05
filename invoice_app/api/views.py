from rest_framework.viewsets import ModelViewSet
from .serializer import InvoiceSerializer, InvoiceServiceSerializer, ServiceCatalogSerializer
from invoice_app.models import Invoice, InvoiceService, ServiceCatalog
from customer_app.models import Customer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.template.response import TemplateResponse
from rest_framework.decorators import action
from django.shortcuts import render
from company_app.models import Company
from rest_framework import status
from django.db import transaction

# You can onyl see the list of the invoices but you cannot change the invoice
class InvoiceView(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        services_data = data.pop("services", [])

        # 1. Validate and create the invoice (without snapshots)
        data["invoice_number"] = generate_invoice_number()

        # 2. Validate and create the invoice (without snapshots)
        serializer = InvoiceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save(user=request.user)

        # 3. CUSTOMER SNAPSHOT
        customer = invoice.customer
        invoice.customer_name = f"{customer.first_name} {customer.last_name}"
        invoice.customer_address = (
            f"{customer.street} {customer.number}, "
            f"{customer.postcode} {customer.city}"
        )

        # 4. COMPANY SNAPSHOT
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

        # 5. CREATE INVOICE SERVICES
        for service in services_data:
            InvoiceService.objects.create(
            invoice=invoice,
            service_name=service.get("service_name"),

            provision_type=service.get("provision_type"),
            provision_fixed=service.get("provision_fixed"),
            provision_percent=service.get("provision_percent"),
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

        new_status = request.data.get("invoice_status")

        # Validate input
        valid_statuses = dict(Invoice.PaymentStatus.choices).keys()
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid payment_status. Allowed: {list(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status
        invoice.invoice_status = new_status
        invoice.save()

        return Response(
            {"status": f"Payment status updated to: {new_status}"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        invoice = self.get_object()
        
        company = Company.objects.first()
        customer = invoice.customer

        # invoice = self.get_object()
        return render(request, "invoice.html", {
            "company": company, 
            'customer': customer, 
            'invoice': invoice
            })

class InvoiceServiceView(ModelViewSet):
    queryset = InvoiceService.objects.all()
    serializer_class = InvoiceServiceSerializer


def generate_invoice_number():
    """
    Generate a new sequential invoice number with the format: #000001
    
    The function:
    - Extracts the numeric part from existing invoice numbers (after #')
    - Finds the highest existing number
    - Increments it by 1
    - Returns the new number formatted with leading zeros
    """
    from django.db.models import Max
    from django.db.models.functions import Substr, Cast
    from django.db.models import IntegerField

    # Annotate each customer with the numeric portion of customer_number
    # Example: "#000123" → 123
    last_invoice = (
        Invoice.objects
        .annotate(num=Cast(Substr('invoice_number', 3), IntegerField()))
        .aggregate(max_num=Max('num'))['max_num']
    )

    # If at least one number exists, increment it; otherwise start at 1
    next_number = (last_invoice + 1) if last_invoice else 1
    
    # Format result as # + 6-digit zero-padded number
    return f"#{next_number:06d}"

class ServiceCatalogView(ModelViewSet):
    queryset = ServiceCatalog.objects.all()
    serializer_class = ServiceCatalogSerializer

    @action(detail=False, methods=['put'])
    def bulk_update(self, request):

        data = request.data

        errors = []
        saved = []

        with transaction.atomic():
            for index, item in enumerate(data):
                item_id = item.get('id')

                instance = None
                
                if item_id is not None:
                    instance = ServiceCatalog.objects.filter(pk=item_id).first()
                
                serializer = self.get_serializer(
                    instance=instance,
                    data=item,
                    partial=False,
                )

                if serializer.is_valid():
                    obj = serializer.save()
                    saved.append(ServiceCatalogSerializer(obj).data)
                else:
                    errors.append(
                        {
                            'index': index,
                            'error': serializer.errors
                        }
                    )
            
            if errors:
                transaction.set_rollback(True)
                return Response(
                    {
                        'status': 'failed',
                        'message': 'Validation failed. No changes were applied.',
                        'errors': errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        return Response(
            {
                'status': 'OK',
                'count': len(saved),
                'results': saved,
            },
            status=status.HTTP_200_OK,
        )