import requests
from django.conf import settings
from course_app.models import Course
from django.shortcuts import get_object_or_404

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

def get_course_price(course_id):
    course = get_object_or_404(Course, id=course_id)
    return course.price