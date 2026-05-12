from django.urls import path, include
from portal import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('', include('portal.urls')),
    path('accounts/', include('allauth.urls'))
]