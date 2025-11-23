from rest_framework import serializers
from invoice_app.models import Invoice, InvoiceService

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class InvoiceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceService
        fields = '__all__'