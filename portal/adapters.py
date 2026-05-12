import logging
from django.core.exceptions import MultipleObjectsReturned
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    ALLOWED_EMAIL = 'md.tahsinul.islam@g.bracu.ac.bd'

    def _get_social_email(self, sociallogin):
        email = (sociallogin.user.email or '').strip().lower()
        if email:
            return email

        extra_data = getattr(sociallogin.account, 'extra_data', {}) or {}
        email = extra_data.get('email') or extra_data.get('emailAddress')
        if email:
            return str(email).strip().lower()

        return ''

    def _is_allowed_email(self, sociallogin):
        return self._get_social_email(sociallogin) == self.ALLOWED_EMAIL

    def is_open_for_signup(self, request, sociallogin):
        return self._is_allowed_email(sociallogin)

    def authentication_allowed(self, request, sociallogin):
        return self._is_allowed_email(sociallogin)

    def get_app(self, request, provider, client_id=None):
        try:
            return super().get_app(request, provider, client_id)

        except MultipleObjectsReturned:
            apps = SocialApp.objects.filter(provider=provider)

            if client_id:
                apps = apps.filter(client_id=client_id)

            app = apps.order_by('id').first()

            if not app:
                raise

            apps.exclude(pk=app.pk).delete()

            return app