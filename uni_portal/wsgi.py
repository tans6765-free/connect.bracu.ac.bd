import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_portal.settings')
django.setup()

if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput')
    except Exception as e:
        print("Migrate warning:", e)

    # Cleanup any leftover SocialApps
    try:
        from allauth.socialaccount.models import SocialApp
        deleted = SocialApp.objects.filter(provider='google').delete()
        print(f"Cleaned up {deleted[0]} old Google SocialApp(s)")
    except Exception as e:
        print("Cleanup warning:", e)

application = get_wsgi_application()