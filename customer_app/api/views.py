from rest_framework.viewsets import ModelViewSet
from .serializer import CustomerSerializer, CustomerCommentSerializer
from customer_app.models import Customer, CustomerComment
from rest_framework.generics import ListCreateAPIView, UpdateAPIView


class CustomerView(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

 # LIST + CREATE
class CustomerCommentListCreate(ListCreateAPIView):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return CustomerComment.objects.filter(customer_id=self.kwargs['customer_id'])

    def perform_create(self, serializer):
        serializer.save(customer_id=self.kwargs['customer_id'])

 # RETRIEVE + UPDATE
class CustomerCommentDetail(ListCreateAPIView):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return CustomerComment.objects.filter(customer_id=self.kwargs['customer_id'])
