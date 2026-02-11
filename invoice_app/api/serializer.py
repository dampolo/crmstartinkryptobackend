from rest_framework import serializers
from invoice_app.models import Invoice, InvoiceService, ServiceCatalog
from company_app.models import Company
from auth_app.models import User
from invoice_app.invoice_number import GenerateInvoiceNumber


class InvoiceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceService
        fields = ['id', 'service_name', 'provision_type',
                  'provision_fixed', 'provision_percent', 'provision_amount']


class InvoiceSerializer(serializers.ModelSerializer):
    services = InvoiceServiceSerializer(many=True, read_only=True)
    customer = serializers.IntegerField(write_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_type', 'invoice_number', 'invoice_status',

            # customer snapshot
            'user_customer_id',
            'user_customer_first_name', 'user_customer_last_name', 'user_customer_street',
            'user_customer_number', 'user_customer_postcode', 'user_customer_city',


            # company snapshot
            'company_name', 'company_street', 'company_number', 'company_postcode',
            'company_city', 'company_tax_number', 'company_email', 'company_bank',
            'company_bank_account', 'company_swift_code', 'company_logo',

            # invoice totals
            'provision', 'amount', 'investitions_amount', 'value_tax',

            # relations
            'customer', 'user',

            # system fields
            'created_at', 'updated_at', 'is_finalized',

            # SERVICES LAST
            'services'
        ]
        # Read-only fields: CANNOT be set by frontend
        read_only_fields = [
            'id',
            'user',                     # filled from request.user
            'invoice_status',           # default = unpaid
            'invoice_number',
            'created_at',
            'updated_at',
            'is_finalized',

            # Customer snapshot
            'user_customer_id',
            'user_customer_first_name', 'user_customer_last_name', 'user_customer_street',
            'user_customer_number', 'user_customer_postcode', 'user_customer_city',


            # Company snapshot
            'company_name',
            'company_street',
            'company_number',
            'company_postcode',
            'company_city',
            'company_tax_number',
            'company_email',
            'company_bank',
            'company_bank_account',
            'company_swift_code',
            'company_logo',
            'services',
        ]

    def create(self, validated_data):
        request = self.context['request']
        current_user = request.user

        customer_id = validated_data.pop('customer')
        customer = User.objects.get(id=customer_id)

        company = Company.objects.first()

        invoice = Invoice(
            **validated_data,
            user=current_user,
            invoice_number=GenerateInvoiceNumber.generate_invoice_number(),

            # CUSTOMER SNAPSHOT
            user_customer_id=customer_id,
            user_customer_first_name=customer.first_name,
            user_customer_last_name=customer.last_name,
            user_customer_street=customer.street,
            user_customer_number=customer.number,
            user_customer_postcode=customer.postcode,
            user_customer_city=customer.city,

            # COMPANY SNAPSHOT
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

        invoice.save()
        return invoice


class ServiceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCatalog
        fields = ['id', 'service_name', 'provision_type',
                  'provision_fixed', 'provision_percent']
