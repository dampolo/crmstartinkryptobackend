from django.urls import path, include
from .views import CustomerView, CustomerCommentListCreate, CustomerCommentDetail
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customers', CustomerView, basename='customer')


urlpatterns = [
    path('', include(router.urls)),
     # LIST + CREATE
    path('customers/<int:customer_id>/comments/', CustomerCommentListCreate.as_view()),
     # RETRIEVE + UPDATE + DELETE
    path('customers/<int:customer_id>/comments/<int:pk>/', CustomerCommentDetail.as_view())
]
