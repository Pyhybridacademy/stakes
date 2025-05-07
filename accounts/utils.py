from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model

User = get_user_model()

def get_site_url(request):
    """
    Get the site URL including protocol and domain.
    """
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    site_url = f"{protocol}://{current_site.domain}"
    return site_url

def send_activation_email(user, request):
    """
    Send account activation email with verification link.
    """
    current_site = get_current_site(request)
    site_url = get_site_url(request)
    mail_subject = 'Activate your account'
    
    message = render_to_string('accounts/emails/activation_email.html', {
        'user': user,
        'site_url': site_url,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'domain': current_site.domain,
    })
    
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = 'html'
    email.send()

def send_password_reset_email(user, request):
    """
    Send password reset email with reset link.
    """
    current_site = get_current_site(request)
    site_url = get_site_url(request)
    mail_subject = 'Reset your password'
    
    message = render_to_string('accounts/emails/password_reset_email.html', {
        'user': user,
        'site_url': site_url,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'domain': current_site.domain,
    })
    
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = 'html'
    email.send()

def send_email_change_verification(user, request):
    """
    Send email change verification email.
    """
    current_site = get_current_site(request)
    site_url = get_site_url(request)
    mail_subject = 'Verify your new email address'
    
    message = render_to_string('accounts/emails/email_change.html', {
        'user': user,
        'site_url': site_url,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'domain': current_site.domain,
        # Use the new URL name for email change verification
        'verification_url': reverse('accounts:verify_email_change', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
    })
    
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = 'html'
    email.send()

def send_password_change_notification(user, request):
    """
    Send password change notification email.
    """
    site_url = get_site_url(request)
    mail_subject = 'Your password has been changed'
    
    # Get IP address from request
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    message = render_to_string('accounts/emails/password_change_notification.html', {
        'user': user,
        'site_url': site_url,
        'ip_address': ip_address,
    })
    
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = 'html'
    email.send()

def send_welcome_email(user, request):
    """
    Send welcome email after account verification.
    """
    site_url = get_site_url(request)
    mail_subject = 'Welcome to Our Platform!'
    
    message = render_to_string('accounts/emails/welcome_email.html', {
        'user': user,
        'site_url': site_url,
    })
    
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = 'html'
    email.send()

def send_login_notification(user, request):
    """
    Send login notification email.
    """
    site_url = get_site_url(request)
    mail_subject = 'New login to your account'
    
    # Get IP address from request
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    # Get user agent information
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    # Simple user agent parsing (in a real app, you might use a library for this)
    browser = 'Unknown'
    device = 'Unknown'
    
    if 'Mobile' in user_agent:
        device = 'Mobile'
    elif 'Tablet' in user_agent:
        device = 'Tablet'
    else:
        device = 'Desktop'
        
    if 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Chrome' in user_agent:
        browser = 'Chrome'
    elif 'Safari' in user_agent:
        browser = 'Safari'
    elif 'Edge' in user_agent:
        browser = 'Edge'
    elif 'MSIE' in user_agent or 'Trident' in user_agent:
        browser = 'Internet Explorer'
    
    message = render_to_string('accounts/emails/login_notification.html', {
        'user': user,
        'site_url': site_url,
        'ip_address': ip_address,
        'device': device,
        'browser': browser,
        'location': 'Unknown',  # In a real app, you might use IP geolocation
    })
    
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = 'html'
    email.send()

def verify_account_activation_token(uidb64, token):
    """
    Verify the activation token and return the user if valid.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        return user
    return None