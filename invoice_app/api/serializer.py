from rest_framework import serializers
from invoice_app.models import Invoice, InvoiceService

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"
        # Read-only fields: CANNOT be set by frontend
        read_only_fields = [
            "id",
            "user",                     # filled from request.user
            "invoice_status",           # default = unpaid
            "created_at",
            "updated_at",
            "is_finalized",
            "pdf_file",

            # Customer snapshot
            "customer_name",
            "customer_address",

            # Company snapshot
            "company_name",
            "company_street",
            "company_number",
            "company_postcode",
            "company_city",
            "company_tax_number",
            "company_email",
            "company_bank",
            "company_bank_account",
            "company_swift_code",
            "company_logo",
        ]

class InvoiceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceService
        fields = '__all__'