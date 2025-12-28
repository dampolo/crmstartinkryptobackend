from django.db import models
from customer_app.models import Customer
from django.utils.translation import gettext_lazy as _
from auth_app.models import User

class PriceType(models.TextChoices):
    FIXED = 'fixed', _('Fixed Amount (€)')
    PERCENT = 'percent', _('Percentage (%)')

class ServiceCatalog(models.Model):

    name = models.CharField(max_length=200)

    provision_type = models.CharField(
        max_length=20,
        choices=PriceType.choices,
        default=PriceType.FIXED
    )

    # Fixed amount (example: 700.00 €)
    amount_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Percent amount (example: 0.05 = 5%)
    amount_percent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage as decimal (e.g. 0.05 = 5%)"
    )

    def __str__(self):
        return f"{self.name} ({self.price_type})"

class Invoice(models.Model):
    class InvoiceType(models.TextChoices):
        INVOICE = 'invoice', _('Invoice')
        CREDIT_NOTE = 'credit_note', _('Credit Note')

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')       # created but not yet due
        UNPAID = 'unpaid', _('Unpaid')         # overdue / not paid
        PAID = 'paid', _('Paid')               # payment received
        CANCELED = 'canceled', _('Canceled')   # invoice is canceled (storno)

    invoice_number = models.CharField(max_length=50, unique=True)

    invoice_type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.INVOICE
    )
    
    invoice_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID
    )

    customer = models.ForeignKey(
        Customer, 
        related_name='invoices', 
        on_delete=models.PROTECT
    )

    user = models.ForeignKey(
        User, 
        related_name='invoices', 
        on_delete=models.PROTECT
    )
    
     # --- CUSTOMER SNAPSHOT ---
    customer_name = models.CharField(max_length=200)
    customer_address = models.TextField()
    
     # --- COMPANY SNAPSHOT ---
    company_name = models.CharField(max_length=255)
    company_street = models.CharField(max_length=255)
    company_number = models.CharField(max_length=20)
    company_postcode = models.CharField(max_length=10)
    company_city = models.CharField(max_length=100)
    company_tax_number = models.CharField(max_length=50)
    company_email = models.EmailField()
    company_bank = models.CharField(max_length=100)
    company_bank_account = models.CharField(max_length=34)
    company_swift_code = models.CharField(max_length=20)
    company_logo = models.ImageField(upload_to='invoice_company_logos/', null=True, blank=True)

    # --- PDF FILE ---
    pdf_file = models.FileField(upload_to="invoices/", null=True, blank=True)

    # --- STATUS INFO ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_finalized = models.BooleanField(default=False)

    # --- INVOICE TOTALS ---
    provision = models.DecimalField(decimal_places=2, max_digits=10)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    investitions_amount = models.DecimalField(decimal_places=2, max_digits=10)
    value_tax = models.DecimalField(decimal_places=2, max_digits=10)
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
class InvoiceService(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        related_name="services",
        on_delete=models.PROTECT
    )

    # CUSTOM service name (frontend-defined or copied from catalog)
    service_name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    # Price type (fixed or percent)
    provision_type = models.CharField(
        max_length=20,
        choices=PriceType.choices,
        default=PriceType.FIXED
    )

     # If FIXED → this field is used
    provision_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # If PERCENT → this field is used
    provision_percent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage as decimal (e.g. 0.05 = 5%)"
    )
    # PRICE for this line item
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"Invoice {self.service_name}"