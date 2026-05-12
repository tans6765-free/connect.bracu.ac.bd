import logging
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    ALLOWED_EMAIL = 'md.tahsinul.islam@g.bracu.ac.bd'

    def _get_social_email(self, sociallogin):
        email = (getattr(sociallogin.user, 'email', '') or '').strip().lower()
        if email:
            return email

        extra_data = getattr(sociallogin.account, 'extra_data', {}) or {}
        email = (
            extra_data.get('email')
            or extra_data.get('emailAddress')
            or extra_data.get('profileObj', {}).get('email')
        )
        if not email and isinstance(extra_data.get('emails'), (list, tuple)):
            first_email = extra_data['emails'][0] if extra_data['emails'] else {}
            email = first_email.get('value') or first_email.get('email')

        if email:
            return str(email).strip().lower()

        return ''

    def pre_social_login(self, request, sociallogin):
        email = self._get_social_email(sociallogin)
        if email != self.ALLOWED_EMAIL:
            logger.warning(f"Blocked Google login for unauthorized email: {email}")
            return

        if sociallogin.is_existing:
            return

        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = User(
                email=email,
                username=email,
                first_name=(sociallogin.account.extra_data.get('given_name') or '').strip(),
                last_name=(sociallogin.account.extra_data.get('family_name') or '').strip(),
            )
            user.set_unusable_password()
            user.save()

        sociallogin.connect(request, user)

    def is_open_for_signup(self, request, sociallogin):
        return self._get_social_email(sociallogin) == self.ALLOWED_EMAIL

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