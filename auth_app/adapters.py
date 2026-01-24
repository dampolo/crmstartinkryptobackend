from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from customer_app.api.serializer import generate_customer_number

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Automatically link social account to existing user
        if email matches.
        """

        # If user already logged in → nothing to do
        if request.user.is_authenticated:
            return

        # Get email from provider
        email = sociallogin.account.extra_data.get("email")
        if not email:
            return

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        # Link social account to existing user
        sociallogin.connect(request, user)

    def save_user(self, request, sociallogin, form=None):
        """
        Called only when a NEW social user is created.
        """
        user = super().save_user(request, sociallogin, form)

        # First-time Google signup logic
        user.customer_number = generate_customer_number()
        user.user_type = 'customer'

        user.save()
        return user