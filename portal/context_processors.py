"""
Context processors for portal app templates
"""
import os


def google_oauth(request):
    """
    Add Google OAuth settings to template context
    """
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    return {
        'google_client_id': google_client_id,
    }
