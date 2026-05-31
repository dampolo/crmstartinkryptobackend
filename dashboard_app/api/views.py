from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_app.models import User
from invoice_app.models import Invoice

class DashboardAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'customers_count': User.objects.filter(role=User.ProfileType.CUSTOMER).count(),
            'applicants_count': User.objects.filter(role=User.ProfileType.APPLICANT).count(),
            'invioces_count': Invoice.objects.count()
        })