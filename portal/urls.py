from django.urls import path
from portal import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('grade-sheet/', views.grade_sheet, name='grade_sheet'),
    path('grade-sheet/pdf/', views.grade_sheet_pdf, name='grade_sheet_pdf'),
    path('grade-sheet/download/', views.grade_sheet_download, name='grade_sheet_download'),
    path('logout/', views.logout_view, name='custom_logout'),
]
