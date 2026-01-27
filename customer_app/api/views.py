from rest_framework.viewsets import ModelViewSet
from .serializer import CustomerSerializer, CustomerCommentSerializer
from customer_app.models import UserComment
from auth_app.models import User

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView

class CustomerView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomerSerializer

class CustomerProfileView(RetrieveUpdateAPIView):
    serializer_class = CustomerSerializer
    def get_object(self):
        return self.request.user

 # LIST + CREATE
class CustomerCommentListCreate(ListCreateAPIView):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return UserComment.objects.filter(customer_id=self.kwargs['customer_id'])

 # RETRIEVE + UPDATE
class CustomerCommentDetail(RetrieveUpdateAPIView):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return UserComment.objects.filter(customer_id=self.kwargs['customer_id'])
