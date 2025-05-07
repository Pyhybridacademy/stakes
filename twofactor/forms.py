from django import forms
from .models import UserTwoFactorSettings

class TwoFactorSetupForm(forms.Form):
    """
    Form for setting up two-factor authentication.
    """
    method = forms.ChoiceField(
        choices=[('totp', 'Authenticator App'), ('email', 'Email OTP')],
        widget=forms.RadioSelect,
        initial='totp',
        label="Authentication Method"
    )

class TOTPVerificationForm(forms.Form):
    """
    Form for verifying TOTP codes.
    """
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'placeholder': '000000',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        }),
        label="Authentication Code"
    )

class EmailOTPVerificationForm(forms.Form):
    """
    Form for verifying email OTP codes.
    """
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'placeholder': '000000',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        }),
        label="Email Code"
    )

class DisableTwoFactorForm(forms.Form):
    """
    Form for disabling two-factor authentication.
    """
    confirm = forms.BooleanField(
        required=True,
        label="I understand that disabling two-factor authentication will make my account less secure."
    )