import logging
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out
from django.contrib.messages import get_messages

logger = logging.getLogger(__name__)


@receiver(user_logged_out)
def clear_messages_on_logout(sender, request, user, **kwargs):
    """Clear all messages when user logs out."""
    try:
        for message in get_messages(request):
            pass  # consume/clear all messages
        logger.info(f"Cleared messages for logged out user: {user}")
    except Exception as e:
        logger.warning(f"Error clearing messages on logout: {e}")
