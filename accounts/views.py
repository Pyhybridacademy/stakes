from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from .forms import (
    SignupForm, LoginForm, CustomPasswordResetForm, 
    CustomSetPasswordForm, CustomPasswordChangeForm, ProfileUpdateForm, EmailChangeForm
)
from .models import UserProfile
from .tokens import account_activation_token
from .utils import (
    send_activation_email, 
    send_password_reset_email, 
    verify_account_activation_token,
    send_password_change_notification, 
    send_welcome_email,
    send_login_notification,
    send_email_change_verification
)

User = get_user_model()

def signup_view(request):
    """
    Handle user registration and send verification email.
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.is_email_verified = False
            user.save()
            
            # Create user profile if it doesn't exist
            UserProfile.objects.get_or_create(user=user)
            
            # Send activation email
            send_activation_email(user, request)
            
            messages.success(
                request, 
                'Account created successfully. Please check your email to verify your account.'
            )
            return redirect('accounts:login')
    else:
        form = SignupForm()
    
    return render(request, 'accounts/auth/signup.html', {'form': form})

def activate_account_view(request, uidb64, token):
    """
    Verify email and activate new user account.
    """
    user = verify_account_activation_token(uidb64, token)
    
    if user:
        # Only handle new account verification in this view
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save()
            
            # Send welcome email for new accounts
            send_welcome_email(user, request)
            messages.success(request, 'Your email has been verified. You can now log in.')
        else:
            # This is likely an email change verification, but using the wrong URL
            messages.info(request, 'This account is already verified. Please log in.')
        
        return redirect('accounts:login')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('accounts:signup')

def verify_email_change_view(request, uidb64, token):
    """
    Verify changed email address for existing user.
    """
    user = verify_account_activation_token(uidb64, token)
    
    if user:
        user.is_email_verified = True
        user.save()
        
        # Check if the user is already logged in
        if request.user.is_authenticated and request.user.pk == user.pk:
            messages.success(request, 'Your new email address has been verified successfully.')
            return redirect('accounts:profile')
        else:
            messages.success(request, 'Your new email address has been verified. Please log in with your new email.')
            return redirect('accounts:login')
    else:
        messages.error(request, 'Verification link is invalid or has expired.')
        return redirect('accounts:login')

def login_view(request):
    """
    Handle user login.
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Send login notification email
                # You might want to add a user preference to enable/disable these
                send_login_notification(user, request)
                
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        # Form errors will be displayed by the template
    else:
        form = LoginForm()
    
    return render(request, 'accounts/auth/login.html', {'form': form})

def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')

@login_required
def password_change_view(request):
    """
    Handle password change for authenticated users.
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            
            # Send password change notification
            send_password_change_notification(user, request)
            
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/auth/password_change.html', {'form': form})

def password_reset_view(request):
    """
    Handle password reset request and ensure user is logged out afterward.
    """
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                send_password_reset_email(user, request)
            except User.DoesNotExist:
                pass  # Don't leak which email exists
            
            # Always log out the user after initiating a reset
            logout(request)
            messages.success(
                request,
                'Password reset email has been sent. Please check your email.'
            )
            return redirect('accounts:login')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'accounts/auth/password_reset.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
    """
    Handle password reset confirmation.
    """
    user = verify_account_activation_token(uidb64, token)
    
    if not user:
        messages.error(request, 'Password reset link is invalid or has expired.')
        return redirect('accounts:password_reset')
    
    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been reset. You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomSetPasswordForm(user)
    
    return render(request, 'accounts/auth/password_reset_confirm.html', {'form': form})

@login_required
def profile_view(request):
    """
    Display user profile.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'accounts/profile/profile.html', {'profile': profile})

@login_required
def profile_update_view(request):
    """
    Update user profile information with AJAX support.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        # Check if request is AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        form = ProfileUpdateForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            # Update user fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.username = form.cleaned_data['username']
            request.user.save()
            
            # Update profile fields
            form.save(commit=False)
            profile.bio = form.cleaned_data['bio']
            profile.location = form.cleaned_data['location']
            profile.date_of_birth = form.cleaned_data['date_of_birth']
            profile.save()
            
            # For regular requests, add a message and redirect
            if not is_ajax:
                messages.success(request, 'Your profile has been updated.')
                return redirect('accounts:profile')
            
            # For AJAX requests, return JSON or redirect response
            # Django will automatically return a redirect response that the fetch API can detect
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
        else:
            # Form is invalid
            if is_ajax:
                # Return form errors as JSON
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': {field: errors for field, errors in form.errors.items()}
                })
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)
    
    return render(request, 'accounts/profile/edit_profile.html', {'form': form, 'profile': profile})

@login_required
def profile_images_update_view(request):
    """
    Update user profile images (avatar and cover photo) with AJAX support.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        # Check if request is AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Variables to track changes
        avatar_updated = False
        cover_updated = False
        
        # Handle avatar update
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            avatar_updated = True
        
        # Handle cover photo update
        if 'cover_photo' in request.FILES:
            profile.cover_photo = request.FILES['cover_photo']
            cover_updated = True
        
        # Save changes if any
        if avatar_updated or cover_updated:
            profile.save()
            
            # Create appropriate success message
            if avatar_updated and cover_updated:
                success_msg = "Your profile picture and cover photo have been updated."
            elif avatar_updated:
                success_msg = "Your profile picture has been updated."
            else:
                success_msg = "Your cover photo has been updated."
            
            # For regular requests, add a message and redirect
            if not is_ajax:
                messages.success(request, success_msg)
                return redirect('accounts:profile')
            
            # For AJAX requests, return JSON response
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'redirect_url': reverse('accounts:profile')
            })
        else:
            # No files were uploaded
            error_msg = "No images were selected for upload."
            
            if not is_ajax:
                messages.info(request, error_msg)
                return redirect('accounts:profile_edit_images')
            
            return JsonResponse({
                'success': False,
                'message': error_msg
            })
    
    # GET request - display the form
    return render(request, 'accounts/profile/edit_profile_images.html', {'profile': profile})

@login_required
def email_change_view(request):
    """
    Handle email change request.
    """
    if request.method == 'POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            
            # Store the new email temporarily
            old_email = request.user.email
            request.user.email = new_email
            request.user.is_email_verified = False
            request.user.save()
            
            # Send verification email using the new function
            send_email_change_verification(request.user, request)
            
            messages.success(
                request, 
                f'Email change requested. We\'ve sent a verification link to {new_email}. '
                f'Your email will not be changed until you verify the new address. '
                f'If you don\'t verify within 24 hours, your email will remain as {old_email}.'
            )
            return redirect('accounts:profile')
    else:
        form = EmailChangeForm(request.user)
    
    return render(request, 'accounts/auth/email_change.html', {'form': form})