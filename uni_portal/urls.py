from django.urls import path, include
from django.contrib.auth.views import LogoutView
from portal import views

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # Portal routes
    path('', include('portal.urls')),
    
    # Override allauth logout to ensure proper session cleanup
    # This is CRITICAL for proper logout functionality
    path('accounts/logout/', 
         LogoutView.as_view(next_page='/accounts/login/'), 
         name='account_logout'),
    
    # All other allauth URLs (login, signup, social auth, etc.)
    path('accounts/', include('allauth.urls')),
]
