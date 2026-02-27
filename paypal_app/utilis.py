import requests
from django.conf import settings
from course_app.models import Course, DiscountCode
from django.shortcuts import get_object_or_404
from invoice_app.models import Tax
from decimal import Decimal
from decimal import ROUND_HALF_UP

def get_paypal_access_token():
    url = f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token"
    headers = {"Accept": "application/json"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(
        url,
        headers=headers,
        data=data,
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
    )

    return response.json()["access_token"]

# Belong to create_order
def create_paypal_order(amount):
    access_token = get_paypal_access_token()

    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "EUR",
                    "value": str(amount),
                }
            }
        ],
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


def capture_paypal_order(order_id):
    access_token = get_paypal_access_token()

    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(url, headers=headers)
    return response.json()

def get_course_price(course_id, discount_id):
    course = get_object_or_404(Course, id=course_id)
    discount = DiscountCode.objects.filter(id=discount_id).first()

    tax = Tax.objects.first()
    tax_percent = tax.percent
    net_price = course.price

    discount_amount_value = 0
    discount_percent_value = 0
    net_price_after_discount = 0
    tax_amount = 0

    if discount:
        if not discount.active:
            raise ValueError('Discount code is not active.')

        discount_amount = (
            net_price * discount.percent_value / Decimal('100')
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        discount_amount_value = discount_amount

        tax_amount_with_discount = (
            (net_price - discount_amount)  * tax_percent / Decimal('100')
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        tax_amount = tax_amount_with_discount
        
        net_price_after_discount = net_price - discount_amount + tax_amount
    else:
        tax_amount_without_discount = (
            net_price  * tax_percent / Decimal('100')
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        tax_amount = tax_amount_without_discount

        net_price_after_discount = net_price + tax_amount_without_discount

    gross_price = (
        net_price_after_discount
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return gross_price