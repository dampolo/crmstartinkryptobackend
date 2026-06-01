from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_app.models import User
from invoice_app.models import Invoice

class DashboardCrmAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        latest_customers = (
            User.objects
            .filter(role=User.ProfileType.CUSTOMER)
            .order_by('-updated_at')[:3]
            .values(
                'first_name',
                'last_name',
                'email',
                'has_portfolio',
            )
        ),
        latest_invoices = (
            Invoice.objects
            .order_by('-updated_at')[:3]
            .values(
                'invoice_number',
                'user_customer_first_name',
                'user_customer_last_name',
                'invoice_status',
                'amount'
            )
        )
        return Response({
            'customers_count': User.objects.filter(role=User.ProfileType.CUSTOMER).count(),
            'applicants_count': User.objects.filter(role=User.ProfileType.APPLICANT).count(),
            'invioces_count': Invoice.objects.count(),
            'latest_customers': list(latest_customers),
            'latest_invoices': list(latest_invoices)
        })