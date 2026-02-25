from django.urls import path
from . import views


urlpatterns = [
    path("paypal/create-order/", views.create_order),
    path("paypal/capture-order/<str:order_id>/", views.capture_order),

]
