import os
import logging
from django.core.exceptions import MultipleObjectsReturned
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings

logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """Allow BrACU emails + Gmail for testing"""
        try:
            email = sociallogin.account.extra_data.get('email')
            if not email:
                email = sociallogin.account.extra_data.get('emailAddress')
            if not email:
                emails = sociallogin.account.extra_data.get('emails') or sociallogin.account.extra_data.get('emailAddresses')
                if isinstance(emails, (list, tuple)) and emails:
                    first = emails[0]
                    if isinstance(first, str):
                        email = first
                    elif isinstance(first, dict):
                        email = first.get('value') or first.get('email') or first.get('address')
            if not email:
                email = getattr(sociallogin.user, 'email', None)
            email = (email or '').lower().strip()

            logger.info(f"[OAuth] Checking signup for email: {email}, provider: {sociallogin.account.provider}, extra_data keys: {list(sociallogin.account.extra_data.keys())}")

            if not email:
                logger.warning(f"[OAuth] No email found in extra_data or user object")
                return False

            # Allow everything in DEBUG mode or on Vercel for testing
            if settings.DEBUG or os.environ.get('VERCEL'):
                logger.info(f"[OAuth] DEBUG or VERCEL mode - allowing signup for {email}")
                return True

            # Production: Only BrACU emails
            if email.endswith('@g.bracu.ac.bd') or email.endswith('@bracu.ac.bd'):
                logger.info(f"[OAuth] BrACU email allowed: {email}")
                return True

            logger.warning(f"[OAuth] Email {email} not in allowed domains")
            return False
        except Exception as e:
            logger.exception(f"[OAuth] Error in is_open_for_signup: {e}")
            return False

    def authentication_allowed(self, request, sociallogin):
        """This is the key method that blocks login"""
        try:
            result = self.is_open_for_signup(request, sociallogin)
            logger.info(f"[OAuth] authentication_allowed returning: {result}")
            return result
        except Exception as e:
            logger.exception(f"[OAuth] Error in authentication_allowed: {e}")
            return False

    def get_app(self, request, provider, client_id=None):
        """Return a single SocialApp row and clean up duplicates if found."""
        try:
            logger.info(f"[OAuth] get_app called for provider={provider}, client_id={client_id}")
            return super().get_app(request, provider, client_id)
        except MultipleObjectsReturned:
            logger.warning(f"[OAuth] Multiple SocialApp rows found for provider={provider}, cleaning up")
            apps = SocialApp.objects.filter(provider=provider)
            if client_id:
                apps = apps.filter(client_id=client_id)
            app = apps.order_by('id').first()
            if not app:
                logger.error(f"[OAuth] No SocialApp found after filter for provider={provider}")
                raise
            logger.info(f"[OAuth] Deleting duplicate SocialApp rows, keeping id={app.id}")
            deleted_count = apps.exclude(pk=app.pk).delete()[0]
            logger.info(f"[OAuth] Deleted {deleted_count} duplicate(s)")
            return app
        except Exception as e:
            logger.exception(f"[OAuth] Error in get_app: {e}")
            raise
