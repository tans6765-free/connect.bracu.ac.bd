from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return False
        if settings.DEBUG:
            return True
        return email.lower().endswith('@g.bracu.ac.bd')

    def authentication_allowed(self, request, sociallogin):
        return self.is_open_for_signup(request, sociallogin)