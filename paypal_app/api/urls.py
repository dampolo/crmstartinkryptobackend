from django.urls import path
from . import views
from paypal_app.api import views

urlpatterns = [
    path("paypal/create-order/", views.CreateOrderView.as_view()),
    path("paypal/capture-order/", views.CaptureOrderView.as_view()),

]
