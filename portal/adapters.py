from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Restrict Google login to @g.bracu.ac.bd email addresses.
    Change ALLOWED_DOMAIN below or set ALLOWED_EMAIL_DOMAIN in settings
    to restrict to a different domain.
    """
    ALLOWED_DOMAIN = getattr(settings, 'ALLOWED_EMAIL_DOMAIN', 'g.bracu.ac.bd')

    def _email_allowed(self, email):
        if not email:
            return False
        return email.lower().endswith('@' + self.ALLOWED_DOMAIN)

    def is_open_for_signup(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email') or sociallogin.user.email
        return self._email_allowed(email)

    def authentication_allowed(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email') or sociallogin.user.email
        return self._email_allowed(email)
