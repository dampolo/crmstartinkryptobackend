from rest_framework import serializers
from purchase_app.models import Purchase

class CustomerPurchasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fileds = ['invoice', 'customer', 'payment_method', 'course', 'discount', 'total', 'status' ]