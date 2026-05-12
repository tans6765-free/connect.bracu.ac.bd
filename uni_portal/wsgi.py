import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_portal.settings')

# ====================== FORCE CLEANUP GOOGLE SOCIALAPP ======================
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("DELETE FROM socialaccount_socialapp WHERE provider = 'google';")
    print("✅ Cleaned all Google SocialApp records (preventing MultipleObjectsReturned)")

application = get_wsgi_application()