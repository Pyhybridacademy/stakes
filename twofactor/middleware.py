from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import UserTwoFactorSettings

class TwoFactorMiddleware:
    """
    Middleware to check if 2FA verification is needed.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require 2FA verification
        self.exempt_paths = [
            '/twofactor/verify/',
            '/twofactor/verify/email/request/',
            '/accounts/logout/',
            '/admin/logout/',
            '/static/',
            '/media/',
        ]

    def __process_request(self, request):
        """
        Process the request to check if 2FA verification is needed.
        """
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None
        
        # Check if the path is exempt
        path = request.path
        if any(path.startswith(exempt_path) for exempt_path in self.exempt_paths):
            return None
        
        # Check if user has 2FA enabled and needs verification
        try:
            two_factor_settings = UserTwoFactorSettings.objects.get(user=request.user, is_enabled=True)
            if two_factor_settings.needs_verification():
                # Store the current URL for redirection after verification
                request.session['next_url'] = request.get_full_path()
                messages.info(request, "Please verify your identity with two-factor authentication.")
                return redirect('twofactor:verify_2fa')
        except UserTwoFactorSettings.DoesNotExist:
            pass
        
        return None

    def __call__(self, request):
        response = self.__process_request(request)
        if response:
            return response
        return self.get_response(request)