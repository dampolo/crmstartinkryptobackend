from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerView, basename='customer')


urlpatterns = [
    path('', include(router.urls)),

    path('profile-customer/', views.CustomerProfileView.as_view()),
     # LIST + CREATE
    path('customers/<int:customer_id>/comments/', views.CustomerCommentListCreate.as_view()),
     # RETRIEVE + UPDATE
    path('customers/<int:customer_id>/comments/<int:pk>/', views.CustomerCommentDetail.as_view()),

    # Invoices from Customer
    path('my-invoices/', views.CustomerInvoicesAPI.as_view(), name='customer-invoices')
]
