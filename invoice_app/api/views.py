from rest_framework.viewsets import ModelViewSet
from .serializer import InvoiceSerializer, InvoiceServiceSerializer
from invoice_app.models import Invoice
from customer_app.models import Customer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.template.response import TemplateResponse
from rest_framework.decorators import action
from django.shortcuts import render
from company_app.models import Company


# You can onyl see the list of the invoices but you cannot change the invoice
class InvoiceView(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        services_data = data.pop('services', [])
        
        # 1. Validate invoice fields
        serializer = InvoiceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()

        # 2. Create snapshot fields
        customer = invoice.customer
        invoice.customer_name = f"{customer.first_name} {customer.last_name}"
        invoice.customer_address = f"{customer.street} {customer.number}, {customer.postcode} {customer.city}"
        invoice.save()

        for service in services_data:
            InvoiceSerializer.object.create(
                invoice=invoice,
                service_catalog=service.get('service_catalog'),
                custom_service_name=service.get("custom_service_name"),
                

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