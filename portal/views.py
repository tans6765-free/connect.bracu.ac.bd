from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
import os
from django.conf import settings
import json


def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp

        try:
            site = Site.objects.get(pk=1)
            site_domain = site.domain if site else 'N/A'
        except:
            site_domain = 'N/A'
        
        try:
            google_app = SocialApp.objects.filter(provider='google').first()
            if google_app:
                google_configured = 'configured'
                google_client_id = google_app.client_id[:10] + '...' if google_app.client_id else 'EMPTY'
                google_has_secret = 'YES' if google_app.secret else 'NO'
                google_sites = list(google_app.sites.values_list('domain', flat=True))
            else:
                google_configured = 'not_configured'
                google_client_id = 'NO_APP'
                google_has_secret = 'N/A'
                google_sites = []
        except Exception as e:
            google_configured = 'error_checking'
            google_client_id = str(e)
            google_has_secret = 'ERROR'
            google_sites = []

        response_data = {
            'status': 'ok',
            'site': site_domain,
            'google_oauth': google_configured,
            'google_client_id': google_client_id,
            'google_has_secret': google_has_secret,
            'google_sites': google_sites,
            'debug': settings.DEBUG,
            'vercel': 'YES' if os.environ.get('VERCEL') else 'NO',
        }
        if request.GET.get('debug') == '1' and os.environ.get('VERCEL'):
            try:
                with open('/tmp/vercel_exception.txt', 'r', encoding='utf-8') as f:
                    response_data['last_exception'] = f.read()
            except Exception as e:
                response_data['last_exception'] = f'Error reading exception log: {e}'
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'debug': settings.DEBUG,
        }, status=500)


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
def grade_sheet_preview(request):
    return render(request, 'grade_sheet.html', {'show_preview': True})


@login_required
def grade_sheet_pdf(request):
    pdf_path = os.path.join(settings.BASE_DIR, 'portal', 'static', 'grade_sheet.pdf')
    if not os.path.exists(pdf_path):
        raise Http404("Grade sheet PDF not found.")
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return response


@login_required
def grade_sheet_download(request):
    pdf_path = os.path.join(settings.BASE_DIR, 'portal', 'static', 'grade_sheet.pdf')
    if not os.path.exists(pdf_path):
        raise Http404("Grade sheet PDF not found.")
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grade_sheet.pdf"'
    return response
