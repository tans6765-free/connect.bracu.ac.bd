import os
import logging
from django.core.exceptions import MultipleObjectsReturned
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings

logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """Allow all signups for testing - restrictions removed"""
        logger.info(f"[OAuth] is_open_for_signup called - ALLOWING ALL (no restrictions)")
        return True

    def authentication_allowed(self, request, sociallogin):
        """Allow all authentication for testing"""
        logger.info(f"[OAuth] authentication_allowed called - ALLOWING ALL")
        return True

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
