from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from customer_app.customer_nummer import GenerateCustomerNumber

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email
        if not email:
            return
        
        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        Called only when a NEW social user is created.
        """
        user = super().save_user(request, sociallogin, form)

        # First-time Google signup logic
        user.customer_number = GenerateCustomerNumber.generate_customer_number()
        user.user_type = 'customer'

        # Google avatar
        # extra_data = sociallogin.account.extra_data
        # picture = extra_data.get('picture')

        # if picture and not user.image:
            # user.image = picture

        user.save()
        return user