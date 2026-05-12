import os


def google_oauth(request):
    """Add Google client ID to templates"""
    return {
        'google_client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
    }