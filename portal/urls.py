from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('grade-sheet/', views.grade_sheet, name='grade_sheet'),
    path('grade-sheet/preview/', views.grade_sheet_preview, name='grade_sheet_preview'),
    path('grade-sheet/download/', views.grade_sheet_download, name='grade_sheet_download'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
