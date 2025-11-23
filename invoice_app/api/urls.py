from django.urls import path, include
from .views import InvoiceServiceView, InvoiceView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'invoices', InvoiceView, basename='invoices')
router.register(r'invoice-services', InvoiceServiceView, basename='invoice-services')

urlpatterns = [
    path('', include(router.urls)),
]