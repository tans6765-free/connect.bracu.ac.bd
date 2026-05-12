import logging
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_updated
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

logger = logging.getLogger(__name__)

def ensure_correct_site_config():
    """Ensure site domain and SocialApp are correctly configured"""
    try:
        site, _ = Site.objects.get_or_create(id=1)
        if site.domain != 'connectbracuacbd.vercel.app':
            logger.warning(f"[Fix] Fixing site domain from '{site.domain}' to 'connectbracuacbd.vercel.app'")
            site.domain = 'connectbracuacbd.vercel.app'
            site.name = 'BracU Portal'
            site.save()
        
        # Ensure Google SocialApp is linked to the correct site
        google_apps = SocialApp.objects.filter(provider='google')
        for app in google_apps:
            if not app.sites.filter(id=1).exists():
                logger.warning(f"[Fix] Adding site to Google SocialApp")
                app.sites.add(site)
    except Exception as e:
        logger.exception(f"[Fix] Error in ensure_correct_site_config: {e}")


@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    """Log OAuth data before authentication"""
    try:
        ensure_correct_site_config()
        logger.info(f"[Signal] pre_social_login triggered")
        logger.info(f"[Signal] Provider: {sociallogin.account.provider}")
        logger.info(f"[Signal] UID: {sociallogin.account.uid}")
        logger.info(f"[Signal] Extra data keys: {list(sociallogin.account.extra_data.keys())}")
        logger.info(f"[Signal] Email from extra_data: {sociallogin.account.extra_data.get('email')}")
        logger.info(f"[Signal] User email: {getattr(sociallogin.user, 'email', 'N/A')}")
        logger.info(f"[Signal] User first_name: {getattr(sociallogin.user, 'first_name', 'N/A')}")
        logger.info(f"[Signal] User last_name: {getattr(sociallogin.user, 'last_name', 'N/A')}")
        logger.info(f"[Signal] Full extra_data: {sociallogin.account.extra_data}")
    except Exception as e:
        logger.exception(f"[Signal] Error in pre_social_login_handler: {e}")


@receiver(social_account_updated)
def social_account_updated_handler(sender, request, sociallogin, **kwargs):
    """Log OAuth account updates"""
    try:
        logger.info(f"[Signal] social_account_updated triggered for {sociallogin.account.provider}")
    except Exception as e:
        logger.exception(f"[Signal] Error in social_account_updated_handler: {e}")
