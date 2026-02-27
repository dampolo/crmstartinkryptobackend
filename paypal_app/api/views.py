from rest_framework.decorators import api_view
from rest_framework.response import Response
from paypal_app.utilis import create_paypal_order, capture_paypal_order, get_course_price


@api_view(["POST"])
def create_order(request):
    course_id = request.data.get("course_id")

    amount = get_course_price(course_id)

    order = create_paypal_order(amount)
    return Response({
        "orderID": order["id"]
    })


@api_view(["POST"])
def capture_order(request):
    order_id = request.data.get("orderID")
    capture = capture_paypal_order(order_id)
    print('#################################################')
    # TODO: verify payment status and update DB

    return Response(capture)