from rest_framework.decorators import api_view
from rest_framework.response import Response
from paypal_app.utilis import create_paypal_order, capture_paypal_order, get_course_price
from django.db import transaction
from auth_app.models import User
from invoice_app.models import Invoice
from invoice_app.invoice_number import GenerateInvoiceNumber
from company_app.models import Company
from rest_framework import views


class CreateOrderView(views.APIView):
    def post(self, request, *args, **kwargs):
        course = request.data.get('course_id')
        discount = request.data.get('discount')
        print(f'{course, discount}')
        amount = get_course_price(course, discount)

        order = create_paypal_order(amount)
        return Response({
            "orderID": order["id"]
        })


class CaptureOrderView(views.APIView):
    def post(self, request, *args, **kwargs):
        customer = request.user
        order_id = request.data.get('orderID')
        course = request.data.get('course_id')
        discount = request.data.get('discount')

        capture = capture_paypal_order(order_id)
        
        company = Company.objects.first()
        

        return Response(capture)