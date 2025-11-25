from rest_framework.viewsets import ModelViewSet
from .serializer import CustomerSerializer, CustomerCommentSerializer
from customer_app.models import Customer, CustomerComment


class CustomerView(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CustomerCommentViewSet(ModelViewSet):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return CustomerComment.objects.filter(customer_id=self.kwargs.get('customer_pk'))

    def perform_create(self, serializer):
        serializer.save(customer_id=self.kwargs.get('customer_pk'))
