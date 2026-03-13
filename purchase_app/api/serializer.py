from rest_framework import serializers
from purchase_app.models import Purchase

class CustomerPurchasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['invoice', 'customer', 'payment_method', 'course', 'discount', 'total', 'status' ]