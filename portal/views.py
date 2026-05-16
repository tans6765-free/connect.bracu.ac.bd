from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.messages import get_messages
from django.http import FileResponse, Http404, JsonResponse
import os
from django.conf import settings


def health_check(request):
    """Health check endpoint — shows OAuth config status."""
    try:
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp

        try:
            site = Site.objects.get(pk=1)
            site_domain = site.domain
        except Exception:
            site_domain = 'N/A'

        try:
            google_app = SocialApp.objects.filter(provider='google').first()
            if google_app:
                google_status = 'configured'
                google_client_id = google_app.client_id[:20] + '...' if google_app.client_id else 'EMPTY'
                google_has_secret = 'YES' if google_app.secret else 'NO'
                google_sites = list(google_app.sites.values_list('domain', flat=True))
            else:
                google_status = 'not_configured'
                google_client_id = 'NO_APP'
                google_has_secret = 'N/A'
                google_sites = []
        except Exception as e:
            google_status = 'error'
            google_client_id = str(e)
            google_has_secret = 'ERROR'
            google_sites = []

        env_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        env_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

        response_data = {
            'status': 'ok',
            'site': site_domain,
            'google_oauth_db': google_status,
            'google_client_id_db': google_client_id,
            'google_has_secret_db': google_has_secret,
            'google_sites': google_sites,
            'env_client_id_set': 'YES' if env_client_id else 'NO',
            'env_secret_set': 'YES' if env_secret else 'NO',
            'debug': settings.DEBUG,
            'vercel': 'YES' if os.environ.get('VERCEL') else 'NO',
        }

        if request.GET.get('debug') == '1' and os.environ.get('VERCEL'):
            try:
                with open('/tmp/vercel_exception.txt', 'r', encoding='utf-8') as f:
                    response_data['last_exception'] = f.read()
            except Exception as e:
                response_data['last_exception'] = f'No exception log: {e}'

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


def logout_view(request):
    """Custom logout — clears messages then redirects to login."""
    logout(request)
    for message in get_messages(request):
        pass  # consume/clear
    return redirect('/accounts/login/')


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def grade_sheet(request):
    return render(request, 'grade_sheet.html')


@login_required
def grade_sheet_pdf(request):
    pdf_path = os.path.join(settings.BASE_DIR, 'portal', 'static', 'grade_sheet.pdf')
    if not os.path.exists(pdf_path):
        raise Http404("Grade sheet PDF not found.")
    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')


@login_required
def grade_sheet_download(request):
    pdf_path = os.path.join(settings.BASE_DIR, 'portal', 'static', 'grade_sheet.pdf')
    if not os.path.exists(pdf_path):
        raise Http404("Grade sheet PDF not found.")
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grade_sheet.pdf"'
    return response
