from django.db import models
from auth_app.models import User
from invoice_app.models import Invoice
from course_app.models import Course, DiscountCode


# -------------------------
# Buy
# -------------------------
class Purchase(models.Model):
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
        DiscountCode, on_delete=models.SET_NULL, null=True, blank=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.first_name}, {self.customer.last_name}"
