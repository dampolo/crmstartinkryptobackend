from rest_framework.viewsets import ModelViewSet
from .serializer import CustomerSerializer, CustomerCommentSerializer, CustomerProfileSerializer
from customer_app.models import UserComment
from auth_app.models import User
from invoice_app.models import Invoice
from invoice_app.api import serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics 
from django.core.exceptions import ValidationError


class CustomerView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomerSerializer

# This method show the whole profile from Customer
class CustomerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    # Customer can see only his profile
    def get_object(self):
        return self.request.user

 # LIST + CREATE
class CustomerCommentListCreate(generics.ListCreateAPIView):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return UserComment.objects.filter(customer_id=self.kwargs['customer_id'])

 # RETRIEVE + UPDATE
class CustomerCommentDetail(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return UserComment.objects.filter(customer_id=self.kwargs['customer_id'])


# If profile is not complete, Customer cannot buy a course
class IsProfileComplete:
    def is_profile_complete(self, request, customer):

        required_fields = [
            "first_name",
            "last_name",
            "street",
            "street_number",
            "postcode",
            "city",
        ]

        missing_fields = [
            field for field in required_fields
            if not getattr(customer, field)
        ]

        if missing_fields:
            raise ValidationError(
                {
                    'message': 'Ergänze dein Profil',
                    "missing_fields": missing_fields
                }
            )

# Customer can see all his Invoices
class CustomerInvoicesAPI(generics.ListAPIView):
    serializer_class = serializer.CustomerInvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(customer=self.request.user)