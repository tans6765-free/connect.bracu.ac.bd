from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('grade-sheet/', views.grade_sheet, name='grade_sheet'),
    path('grade-sheet/preview/', views.grade_sheet_preview, name='grade_sheet_preview'),
    path('grade-sheet/pdf/', views.grade_sheet_pdf, name='grade_sheet_pdf'),
    path('grade-sheet/download/', views.grade_sheet_download, name='grade_sheet_download'),
    # Redirect old /login/ to allauth's login so Google OAuth flow works correctly
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
]
