import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
# from ratelimit.decorators import ratelimit

from .models import UserTwoFactorSettings, EmailOTP
from .forms import TwoFactorSetupForm, TOTPVerificationForm, EmailOTPVerificationForm, DisableTwoFactorForm
from .utils import (
    generate_totp_secret, get_totp_uri, generate_qr_code, verify_totp_code,
    generate_backup_codes, generate_email_otp, send_otp_email, validate_email_otp
)

@login_required
def security_settings(request):
    """
    View for managing security settings, including 2FA.
    """
    # Get or create 2FA settings
    two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(user=request.user)
    
    context = {
        'two_factor_settings': two_factor_settings,
    }
    
    return render(request, 'twofactor/security_settings.html', context)

@login_required
def setup_2fa(request):
    """
    View for setting up 2FA.
    """
    # Get or create 2FA settings
    two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(user=request.user)
    
    # If 2FA is already enabled, redirect to security settings
    if two_factor_settings.is_enabled:
        messages.info(request, "Two-factor authentication is already enabled.")
        return redirect('twofactor:security_settings')
    
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['method']
            
            # Store the method in the session for the next step
            request.session['2fa_setup_method'] = method
            
            if method == 'totp':
                # Generate TOTP secret and store in session
                secret = generate_totp_secret()
                request.session['2fa_setup_secret'] = secret
                
                # Generate QR code
                totp_uri = get_totp_uri(secret, request.user.email)
                qr_code_path = generate_qr_code(totp_uri)
                
                # Store the QR code path in the session
                request.session['2fa_qr_code_path'] = qr_code_path
                
                return redirect('twofactor:setup_totp')
            elif method == 'email':
                # Generate and send OTP
                otp = generate_email_otp(request.user)
                send_otp_email(request.user, otp)
                
                messages.success(request, f"A verification code has been sent to {request.user.email}.")
                return redirect('twofactor:verify_email_otp')
    else:
        form = TwoFactorSetupForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'twofactor/setup_2fa.html', context)

@login_required
def setup_totp(request):
    """
    View for setting up TOTP-based 2FA.
    """
    # Check if we have the necessary session data
    if '2fa_setup_secret' not in request.session or '2fa_qr_code_path' not in request.session:
        messages.error(request, "Setup session expired. Please start again.")
        return redirect('twofactor:setup_2fa')
    
    secret = request.session['2fa_setup_secret']
    qr_code_path = request.session['2fa_qr_code_path']
    
    # Check if the QR code file exists
    if not os.path.exists(qr_code_path):
        messages.error(request, "QR code not found. Please try again.")
        return redirect('twofactor:setup_2fa')
    
    if request.method == 'POST':
        form = TOTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Verify the code
            if verify_totp_code(secret, code):
                # Get or create 2FA settings
                two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(user=request.user)
                
                # Update settings
                two_factor_settings.is_enabled = True
                two_factor_settings.method = 'totp'
                two_factor_settings.totp_secret = secret
                two_factor_settings.backup_codes = generate_backup_codes()
                two_factor_settings.last_verified = timezone.now()
                two_factor_settings.save()
                
                # Clean up session
                if '2fa_setup_secret' in request.session:
                    del request.session['2fa_setup_secret']
                
                # Delete the QR code file
                try:
                    os.remove(qr_code_path)
                except OSError:
                    pass  # Ignore errors
                
                if '2fa_qr_code_path' in request.session:
                    del request.session['2fa_qr_code_path']
                
                messages.success(request, "Two-factor authentication has been enabled successfully.")
                return redirect('twofactor:security_settings')
            else:
                messages.error(request, "Invalid verification code. Please try again.")
    else:
        form = TOTPVerificationForm()
    
    context = {
        'form': form,
        'secret': secret,
        'qr_code_url': reverse('twofactor:qr_code'),
    }
    
    return render(request, 'twofactor/setup_totp.html', context)

@login_required
def qr_code(request):
    """
    View for serving the QR code image.
    """
    if '2fa_qr_code_path' not in request.session:
        raise Http404("QR code not found")
    
    qr_code_path = request.session['2fa_qr_code_path']
    
    if not os.path.exists(qr_code_path):
        raise Http404("QR code not found")
    
    with open(qr_code_path, 'rb') as f:
        return HttpResponse(f.read(), content_type='image/png')

@login_required
def verify_email_otp(request):
    """
    View for verifying email OTP during setup.
    """
    if request.method == 'POST':
        form = EmailOTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Verify the code
            if validate_email_otp(request.user, code):
                # Get or create 2FA settings
                two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(user=request.user)
                
                # Update settings
                two_factor_settings.is_enabled = True
                two_factor_settings.method = 'email'
                two_factor_settings.last_verified = timezone.now()
                two_factor_settings.backup_codes = generate_backup_codes()
                two_factor_settings.save()
                
                messages.success(request, "Two-factor authentication has been enabled successfully.")
                return redirect('twofactor:security_settings')
            else:
                messages.error(request, "Invalid or expired verification code. Please try again.")
                return redirect('twofactor:request_email_otp')
    else:
        form = EmailOTPVerificationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'twofactor/verify_email_otp.html', context)

@login_required
def request_email_otp(request):
    """
    View for requesting a new email OTP.
    """
    # Generate and send OTP
    otp = generate_email_otp(request.user)
    send_otp_email(request.user, otp)
    
    messages.success(request, f"A new verification code has been sent to {request.user.email}.")
    return redirect('twofactor:verify_email_otp')

@login_required
def verify_2fa(request):
    """
    View for verifying 2FA during login.
    """
    # Get 2FA settings
    two_factor_settings = get_object_or_404(UserTwoFactorSettings, user=request.user, is_enabled=True)
    
    # If 2FA is not needed, redirect to the next URL or home
    if not two_factor_settings.needs_verification():
        next_url = request.session.get('next_url', 'home')
        if 'next_url' in request.session:
            del request.session['next_url']
        return redirect(next_url)
    
    if two_factor_settings.method == 'totp':
        if request.method == 'POST':
            form = TOTPVerificationForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                
                # Verify the code
                if verify_totp_code(two_factor_settings.totp_secret, code):
                    # Update last verified
                    two_factor_settings.update_last_verified()
                    
                    # Redirect to the next URL or home
                    next_url = request.session.get('next_url', 'home')
                    if 'next_url' in request.session:
                        del request.session['next_url']
                    
                    messages.success(request, "Two-factor authentication verified successfully.")
                    return redirect(next_url)
                else:
                    messages.error(request, "Invalid verification code. Please try again.")
        else:
            form = TOTPVerificationForm()
        
        context = {
            'form': form,
            'method': 'totp',
        }
        
        return render(request, 'twofactor/verify_2fa.html', context)
    
    elif two_factor_settings.method == 'email':
        # Check if we need to send an OTP
        if request.method == 'GET' and not request.session.get('email_otp_sent'):
            # Generate and send OTP
            otp = generate_email_otp(request.user)
            send_otp_email(request.user, otp)
            
            request.session['email_otp_sent'] = True
            messages.success(request, f"A verification code has been sent to {request.user.email}.")
        
        if request.method == 'POST':
            form = EmailOTPVerificationForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                
                # Verify the code
                if validate_email_otp(request.user, code):
                    # Update last verified
                    two_factor_settings.update_last_verified()
                    
                    # Clean up session
                    if 'email_otp_sent' in request.session:
                        del request.session['email_otp_sent']
                    
                    # Redirect to the next URL or home
                    next_url = request.session.get('next_url', 'home')
                    if 'next_url' in request.session:
                        del request.session['next_url']
                    
                    messages.success(request, "Two-factor authentication verified successfully.")
                    return redirect(next_url)
                else:
                    messages.error(request, "Invalid or expired verification code. Please try again.")
                    return redirect('twofactor:request_verification_otp')
        else:
            form = EmailOTPVerificationForm()
        
        context = {
            'form': form,
            'method': 'email',
        }
        
        return render(request, 'twofactor/verify_2fa.html', context)

@login_required
def request_verification_otp(request):
    """
    View for requesting a new email OTP during verification.
    """
    # Generate and send OTP
    otp = generate_email_otp(request.user)
    send_otp_email(request.user, otp)
    
    request.session['email_otp_sent'] = True
    messages.success(request, f"A new verification code has been sent to {request.user.email}.")
    return redirect('twofactor:verify_2fa')

@login_required
def disable_2fa(request):
    """
    View for disabling 2FA.
    """
    # Get 2FA settings
    two_factor_settings = get_object_or_404(UserTwoFactorSettings, user=request.user, is_enabled=True)
    
    if request.method == 'POST':
        form = DisableTwoFactorForm(request.POST)
        if form.is_valid():
            # Disable 2FA
            two_factor_settings.is_enabled = False
            two_factor_settings.totp_secret = None
            two_factor_settings.backup_codes = []
            two_factor_settings.save()
            
            messages.success(request, "Two-factor authentication has been disabled.")
            return redirect('twofactor:security_settings')
    else:
        form = DisableTwoFactorForm()
    
    context = {
        'form': form,
        'two_factor_settings': two_factor_settings,
    }
    
    return render(request, 'twofactor/disable_2fa.html', context)

@login_required
def view_backup_codes(request):
    """
    View for displaying backup codes.
    """
    # Get 2FA settings
    two_factor_settings = get_object_or_404(UserTwoFactorSettings, user=request.user, is_enabled=True)
    
    context = {
        'backup_codes': two_factor_settings.backup_codes,
    }
    
    return render(request, 'twofactor/backup_codes.html', context)

@login_required
@require_POST
def regenerate_backup_codes(request):
    """
    View for regenerating backup codes.
    """
    # Get 2FA settings
    two_factor_settings = get_object_or_404(UserTwoFactorSettings, user=request.user, is_enabled=True)
    
    # Generate new backup codes
    two_factor_settings.backup_codes = generate_backup_codes()
    two_factor_settings.save()
    
    messages.success(request, "Backup codes have been regenerated.")
    return redirect('twofactor:view_backup_codes')

@login_required
def change_2fa_method(request):
    """
    View for changing 2FA method.
    """
    # Get 2FA settings
    two_factor_settings = get_object_or_404(UserTwoFactorSettings, user=request.user, is_enabled=True)
    
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['method']
            
            # If changing to the same method, redirect back
            if method == two_factor_settings.method:
                messages.info(request, f"You are already using {method} for two-factor authentication.")
                return redirect('twofactor:security_settings')
            
            # Store the method in the session for the next step
            request.session['2fa_setup_method'] = method
            
            if method == 'totp':
                # Generate TOTP secret and store in session
                secret = generate_totp_secret()
                request.session['2fa_setup_secret'] = secret
                
                # Generate QR code
                totp_uri = get_totp_uri(secret, request.user.email)
                qr_code_path = generate_qr_code(totp_uri)
                
                # Store the QR code path in the session
                request.session['2fa_qr_code_path'] = qr_code_path
                
                return redirect('twofactor:setup_totp')
            elif method == 'email':
                # Generate and send OTP
                otp = generate_email_otp(request.user)
                send_otp_email(request.user, otp)
                
                messages.success(request, f"A verification code has been sent to {request.user.email}.")
                return redirect('twofactor:verify_email_otp')
    else:
        form = TwoFactorSetupForm(initial={'method': two_factor_settings.method})
    
    context = {
        'form': form,
        'two_factor_settings': two_factor_settings,
    }
    
    return render(request, 'twofactor/change_2fa_method.html', context)