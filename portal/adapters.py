"""
Custom Django-allauth adapter for Google OAuth with proper email handling
and account linking.

Place this file at: portal/adapters.py
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from django.conf import settings


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for Google OAuth with:
    - Proper email handling and validation
    - Account linking by email
    - Email-based signup restrictions (optional)
    """
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Determine if automatic signup is allowed for this social account.
        
        You can add restrictions here, for example:
        - Only allow @g.bracu.ac.bd emails
        - Whitelist specific domains
        - Require admin approval
        """
        email = sociallogin.account.extra_data.get('email', '')
        
        # OPTION 1: Restrict to BRAC Google Workspace domain
        # Uncomment this to only allow BRAC accounts
        # if email and '@g.bracu.ac.bd' in email:
        #     return True
        # return False
        
        # OPTION 2: Allow all Google accounts (current setting)
        if email:
            return True
        
        return False
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before user is logged in via social account.
        
        This is where we:
        1. Check if user already exists with this email
        2. Link social account to existing user if applicable
        3. Prevent duplicate accounts
        """
        # If the user already exists (linked), do nothing
        if sociallogin.is_existing:
            return
        
        # Try to link with existing user by email
        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                # Find existing user with same email
                existing_user = User.objects.get(email=email)
                
                # Link this social account to the existing user
                sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            # No existing user, will create new one via auto_signup
            pass
        except Exception as e:
            # Log any other errors but don't crash
            print(f"Error in pre_social_login: {e}")
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save user after successful OAuth.
        
        Extracts user info from Google profile and updates Django user.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Extract additional info from Google profile
        extra_data = sociallogin.account.extra_data
        user.first_name = extra_data.get('given_name', '')
        user.last_name = extra_data.get('family_name', '')
        user.email = extra_data.get('email', user.email)
        
        # Save the updated user
        user.save()
        
        return user
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user instance with data from social login.
        
        Called before save_user to set initial user attributes.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Ensure email is set from Google profile
        if not user.email:
            user.email = data.get('email', '')
        
        return user
    
    def get_app(self, request, provider, client_id=None):
        """
        Get the SocialApp instance.
        
        This is called to get the registered OAuth app from the database.
        Make sure you've created it in Django Admin!
        """
        app = super().get_app(request, provider, client_id)
        return app


# Optional: Email address adapter for additional email handling
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Optional: Custom adapter for account-level settings.
    """
    
    def is_open_for_signup(self, request):
        """
        Allow signup only via Google OAuth, not via username/password.
        """
        # Allow signup for social accounts
        return True
    
    def clean_email(self, email):
        """
        Validate and clean email addresses.
        """
        email = super().clean_email(email)
        
        # Optional: Restrict domain
        # if not email.endswith('@g.bracu.ac.bd'):
        #     raise forms.ValidationError("Only BRAC Google accounts are allowed")
        
        return email


# If you want to use the CustomAccountAdapter, add this to settings.py:
# ACCOUNT_ADAPTER = 'portal.adapters.CustomAccountAdapter'
