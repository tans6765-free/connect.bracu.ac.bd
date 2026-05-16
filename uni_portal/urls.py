from django.urls import path, include
from django.contrib.auth.views import LogoutView
from portal import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),

    # Custom logout (must come BEFORE allauth URLs so it takes priority)
    path('logout/', views.logout_view, name='custom_logout'),

    # Override allauth's own logout to use our custom handler too
    path('accounts/logout/',
         LogoutView.as_view(next_page='/accounts/login/'),
         name='account_logout'),

    # All allauth URLs (login, social auth, etc.)
    path('accounts/', include('allauth.urls')),

    # Portal pages
    path('', include('portal.urls')),
]
