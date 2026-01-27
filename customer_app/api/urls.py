from django.urls import path, include
from .views import CustomerView, CustomerCommentListCreate, CustomerCommentDetail, CustomerProfileView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customers', CustomerView, basename='customer')


urlpatterns = [
    path('', include(router.urls)),

    path('profile-customer/', CustomerProfileView.as_view()),
     # LIST + CREATE
    path('customers/<int:customer_id>/comments/', CustomerCommentListCreate.as_view()),
     # RETRIEVE + UPDATE
    path('customers/<int:customer_id>/comments/<int:pk>/', CustomerCommentDetail.as_view())
]
