from django.urls import path, include
from .views import CustomerView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customers', CustomerView, basename='customer')


urlpatterns = [
    path('', include(router.urls))
]
