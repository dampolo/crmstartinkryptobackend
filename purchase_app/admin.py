from django.contrib import admin
from purchase_app.models import Purchase

# Register your models here.


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'customer', 'course', 'discount', 'price' ]


admin.site.register(Purchase, PurchaseAdmin)
