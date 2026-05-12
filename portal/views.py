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
            google_configured = 'configured' if (google_app and google_app.client_id and google_app.client_id != 'placeholder-client-id') else 'not_configured'
        except:
            google_configured = 'error_checking'
        
        return JsonResponse({
            'status': 'ok',
            'site': site_domain,
            'google_oauth': google_configured,
            'debug': settings.DEBUG,
            'google_env_vars': 'set' if os.environ.get('GOOGLE_CLIENT_ID') else 'missing',
        })
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
def grade_sheet_download(request):
    pdf_path = os.path.join(settings.BASE_DIR, 'portal', 'static', 'grade_sheet.pdf')
    if not os.path.exists(pdf_path):
        raise Http404("Grade sheet PDF not found.")
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grade_sheet.pdf"'
    return response
