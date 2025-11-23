from rest_framework.viewsets import ModelViewSet
from .serializer import InvoiceSerializer, InvoiceServiceSerializer
from invoice_app.models import Invoice
from rest_framework.decorators import action

# You can onyl see the list of the invoices but you cannot change the invoice
class InvoiceView(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

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
    
class InvoiceServiceView(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceServiceSerializer