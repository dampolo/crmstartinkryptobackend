from django.urls import path
from . import views


urlpatterns = [
    path("paypal/create-order/", views.create_order),
    path("paypal/capture-order/", views.capture_order),

]
