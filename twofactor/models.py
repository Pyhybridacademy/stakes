from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

class UserTwoFactorSettings(models.Model):
    """
    Stores user's two-factor authentication settings.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='two_factor')
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(
        max_length=20, 
        choices=[('totp', 'Authenticator App'), ('email', 'Email OTP')],
        default='totp'
    )
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    last_verified = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s 2FA Settings"
    
    def needs_verification(self, verification_window_days=14):
        """
        Check if the user needs to verify 2FA based on the last verification time.
        """
        if not self.is_enabled:
            return False
        
        if not self.last_verified:
            return True
        
        verification_window = datetime.timedelta(days=verification_window_days)
        return timezone.now() > self.last_verified + verification_window
    
    def update_last_verified(self):
        """
        Update the last verified timestamp to now.
        """
        self.last_verified = timezone.now()
        self.save(update_fields=['last_verified'])


class EmailOTP(models.Model):
    """
    Stores email one-time password codes.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email}"
    
    def is_valid(self):
        """
        Check if the OTP is still valid (not expired and not used).
        """
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """
        Mark the OTP as used.
        """
        self.is_used = True
        self.save(update_fields=['is_used'])