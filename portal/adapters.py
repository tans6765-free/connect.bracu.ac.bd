from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    allowed_email = 'md.tahsinul.islam@g.bracu.ac.bd'

    def is_open_for_signup(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email') or sociallogin.user.email
        if email and email.lower() == self.allowed_email:
            return True
        return False

    def authentication_allowed(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email') or sociallogin.user.email
        if email and email.lower() == self.allowed_email:
            return True
        return False