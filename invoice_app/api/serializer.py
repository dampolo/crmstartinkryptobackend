from rest_framework import serializers
from invoice_app.models import Invoice, InvoiceService, ServiceCatalog

class InvoiceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceService
        fields = ["id", "service_name", "provision_type", "provision_fixed", "provision_percent", "amount"]

class ServiceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCatalog
        fields = ["name", "provision_type", "amount_fixed", "amount_percent"]

class InvoiceSerializer(serializers.ModelSerializer):
    services = InvoiceServiceSerializer(many=True, read_only= True)

    class Meta:
        model = Invoice
        fields = [
            "id", "invoice_number","invoice_type", "invoice_status",

            # customer snapshot
            "customer_name", "customer_address",

            # company snapshot
            "company_name", "company_street", "company_number", "company_postcode",
            "company_city", "company_tax_number", "company_email", "company_bank",
            "company_bank_account", "company_swift_code", "company_logo",

            # invoice totals
            "provision", "amount", "investitions_amount", "value_tax",

            # relations
            "customer", "user",

            # system fields
            "pdf_file", "created_at", "updated_at", "is_finalized",

            # SERVICES LAST
            "services"
        ]
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
            'services',
        ]

