import logging
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_updated
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    """Log OAuth data before authentication"""
    try:
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
