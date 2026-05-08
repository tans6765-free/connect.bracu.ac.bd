from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
import os
from django.conf import settings


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
