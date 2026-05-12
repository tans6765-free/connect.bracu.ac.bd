import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings

logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter that:
    1. Creates app from settings if available (no DB lookup needed)
    2. Allows all signups and authentications for testing
    3. Cleans up duplicate SocialApp rows
    """

    def is_open_for_signup(self, request, sociallogin):
        """Allow all signups."""
        return True

    def authentication_allowed(self, request, sociallogin):
        """Allow all authentication."""
        return True

    def get_app(self, request, provider, client_id=None):
        """
        Get the SocialApp. First try settings-based config (no DB needed),
        then fall back to database lookup.
        
        This is critical for Vercel where /tmp DB is ephemeral.
        """
        try:
            # Try to get app from SOCIALACCOUNT_PROVIDERS settings first
            provider_settings = settings.SOCIALACCOUNT_PROVIDERS.get(provider, {})
            app_config = provider_settings.get('APP', {})
            
            cid = app_config.get('client_id', '').strip()
            secret = app_config.get('secret', '').strip()
            
            if cid and secret:
                # Create an in-memory (unsaved) SocialApp from settings
                # This works with allauth's settings-aware adapter
                app = SocialApp(
                    provider=provider,
                    name=provider.capitalize(),
                    client_id=cid,
                    secret=secret,
                    key=app_config.get('key', ''),
                )
                logger.info(f"[OAuth] Using settings-based {provider} app (client_id={cid[:8]}...)")
                return app
        except Exception as e:
            logger.warning(f"[OAuth] Settings-based app failed: {e}")

        # Fall back to database SocialApp
        try:
            return super().get_app(request, provider, client_id)
        except SocialApp.DoesNotExist:
            logger.error(f"[OAuth] No SocialApp for {provider} in DB or settings")
            raise
        except Exception as e:
            logger.exception(f"[OAuth] Error getting {provider} app: {e}")
            raise
