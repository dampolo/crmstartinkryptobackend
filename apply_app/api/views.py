from django.views import View
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import json

@method_decorator(csrf_exempt, name="dispatch")
class ApplyView(View):
    def post(self, request, *args, **kwargs):
        try:
            title = request.POST.get("title")
            first_name = request.POST.get("first-name")
            last_name = request.POST.get("last-name")
            applicant_email = request.POST.get("email")
            phonenumber = request.POST.get("phonenumber")
            file = request.FILES.get("file")
            
            # Build email
            body = {
                "title": title,
                "first_name": first_name,
                "last_name": last_name,
                "email": applicant_email,
                "phonenumber": phonenumber,
            }
            # E-mail to me
            html_to_me = render_to_string("emails/email_to_me.html", body)
            email_message = EmailMessage(
                subject=f"Bewerbung von {first_name} {last_name}",
                body=html_to_me,
                from_email=f"Start in Krypto <{settings.DEFAULT_FROM_EMAIL}>",  # always your verified sender
                to=[settings.DEFAULT_FROM_EMAIL],
            )
            
            if file:
                email_message.attach(file.name, file.read(), file.content_type)

            email_message.content_subtype = "html"
            email_message.send()

            # Confirmation email to USER
            html_answer = render_to_string("emails/email_answer.html", body)
            answer_message = EmailMessage(
                subject="Bestätigung von Start in Krypto",
                body=html_answer,
                from_email=f"Start in Krypto <{settings.DEFAULT_FROM_EMAIL}>",
                to=[applicant_email],
            )
            answer_message.content_subtype = "html"
            answer_message.send()

            return JsonResponse({"message": "Message sent successfully!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get(self, request, *args, **kwargs):
        return JsonResponse({"error": "GET method not allowed"}, status=405)