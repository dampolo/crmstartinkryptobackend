from django.db import models
from django.utils.translation import gettext_lazy as _
from auth_app.models import User

class Customer(models.Model):
    class TitleChoices(models.TextChoices):
        HERR = 'Herr', _('Herr')
        FRAU = 'Frau', _('Frau')
        DIVERS = 'Divers', _('Divers')
    
    user = models.ForeignKey(User, related_name='customer', on_delete=models.PROTECT)
    photo = models.ImageField(upload_to='customers/photos/', blank=True, null=True)
    customer_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=20, choices=TitleChoices)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    street = models.CharField(max_length=200)
    number = models.CharField(max_length=10)
    postcode = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50)
    has_portfolio = models.BooleanField(default=False)
    has_subscription = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_number})"
    
class CustomerComment(models.Model):
    user = models.ForeignKey(
    User,
    related_name='comments',
    on_delete=models.PROTECT,
    null=True,
    blank=True
)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment for {self.customer} on {self.created_at:%Y-%m-%d}"