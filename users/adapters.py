from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email

        if not email:
            return

        try:
            existing_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        if sociallogin.is_existing:
            return

        sociallogin.connect(request, existing_user)
