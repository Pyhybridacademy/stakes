from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import UserProfile
from .widgets import (
    TailwindTextInput, TailwindEmailInput, TailwindPasswordInput,
    TailwindTextarea, TailwindDateInput, TailwindFileInput
)

User = get_user_model()

class SignupForm(UserCreationForm):
    """
    Form for user registration with email as the primary identifier.
    """
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=TailwindTextInput()
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=TailwindTextInput()
    )
    email = forms.EmailField(
        max_length=254, 
        required=True, 
        help_text='Required. Enter a valid email address.',
        widget=TailwindEmailInput()
    )
    username = forms.CharField(
        max_length=150, 
        required=False, 
        help_text='Optional. Letters, digits and @/./+/-/_ only.',
        widget=TailwindTextInput()
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=TailwindPasswordInput(),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        strip=False,
        widget=TailwindPasswordInput(),
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            return None
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        return username


class LoginForm(AuthenticationForm):
    """
    Form for user login using email instead of username.
    """
    username = forms.EmailField(
        label=_("Email"),
        widget=TailwindEmailInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=TailwindPasswordInput(),
    )
    
    error_messages = {
        'invalid_login': _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive. Please verify your email address."),
        'not_verified': _("Please verify your email address before logging in."),
    }
    
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        if not user.is_email_verified:
            raise forms.ValidationError(
                self.error_messages['not_verified'],
                code='not_verified',
            )


class CustomPasswordResetForm(PasswordResetForm):
    """
    Form for requesting a password reset email.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=TailwindEmailInput(attrs={'autocomplete': 'email'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Form for setting a new password after reset.
    """
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=TailwindPasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        strip=False,
        widget=TailwindPasswordInput(attrs={'autocomplete': 'new-password'}),
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with improved styling and error handling.
    """
    old_password = forms.CharField(
        label=_("Current Password"),
        strip=False,
        widget=TailwindPasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    new_password1 = forms.CharField(
        label=_("New Password"),
        strip=False,
        widget=TailwindPasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=None,  # We'll provide our own help text in the template
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        strip=False,
        widget=TailwindPasswordInput(attrs={'autocomplete': 'new-password'}),
    )


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=TailwindTextInput()
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=TailwindTextInput()
    )
    username = forms.CharField(
        max_length=150, 
        required=False,
        widget=TailwindTextInput()
    )
    
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'location', 'date_of_birth')
        widgets = {
            'avatar': TailwindFileInput(),
            'bio': TailwindTextarea(),
            'location': TailwindTextInput(),
            'date_of_birth': TailwindDateInput(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['username'].initial = user.username


class EmailChangeForm(forms.Form):
    """
    Form for changing email address.
    """
    email = forms.EmailField(
        label=_("New email address"),
        max_length=254,
        widget=TailwindEmailInput(attrs={'autocomplete': 'email'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email == self.user.email:
            raise forms.ValidationError(_("This is already your email address."))
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        return email

