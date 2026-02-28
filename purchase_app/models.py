from django.db import models
from auth_app.models import User
from invoice_app.models import Invoice
from course_app.models import Course, DiscountCode
from django.utils.translation import gettext_lazy as _


# -------------------------
# Buy
# -------------------------
class Purchase(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        PAID = 'PAID', _('Paid')
        FAILED = 'FAILED', _('Failed')
        CANCELED = 'CANCELED', _('Canceled')

    invoice = models.OneToOneField(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase'
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        limit_choices_to={'type': User.ProfileType.CUSTOMER}
    )


    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='purchases')

    discount = models.ForeignKey(
        DiscountCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.OPEN
    )

    # 🔒 SNAPSHOT VALUES
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)

    tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2)

    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    total = models.DecimalField(max_digits=8, decimal_places=2)

    paypal_order_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.first_name}, {self.customer.last_name}"
