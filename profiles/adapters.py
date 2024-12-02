from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                if not SocialAccount.objects.filter(user=user, provider=sociallogin.account.provider).exists():
                    sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
