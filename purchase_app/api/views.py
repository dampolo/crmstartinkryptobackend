from rest_framework import generics
from purchase_app.api import serializer
from purchase_app import models
from rest_framework import permissions

# User can see all his purchases
class CustomerPurchasesAPI(generics.ListAPIView):
    serializer_class = serializer.CustomerPurchasesSerializer
    permission_classes =[permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Purchase.objects.filter(customer=self.request.user)