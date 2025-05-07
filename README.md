# Django Authentication System Setup Guide

This guide provides comprehensive instructions for setting up and customizing the Django Authentication System, which includes a core authentication app (`accounts`) and an optional Two-Factor Authentication app (`twofactor`).

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Customization](#customization)
5. [Two-Factor Authentication](#two-factor-authentication)
6. [Integration with Other Apps](#integration-with-other-apps)
7. [Management Commands](#management-commands)
8. [Troubleshooting](#troubleshooting)

## Overview

This authentication system provides a complete solution for user authentication in Django projects. It includes:

- Email-based authentication (instead of username)
- Email verification (for account activation)
- Password reset/change functionality
- User profiles with customizable fields
- Social authentication (Google, Facebook, etc.)
- Optional Two-Factor Authentication (2FA)
- Account security settings and deletion

### Project Structure

The authentication system consists of three main apps:

1. **`accounts`**: Core authentication functionality
2. **`twofactor`**: Optional Two-Factor Authentication
3. **`core`**: Base templates and landing page

## Installation

### Option 1: Start a New Project with This Authentication System

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/django-auth-system.git
   cd django-auth-system

   ```

2. Create and activate a virtual environment:

```shellscript
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```


3. Install dependencies:

```shellscript
pip install -r requirements.txt
```


4. Run migrations:

```shellscript
python manage.py migrate
```


5. Create a superuser:

```shellscript
python manage.py createsuperuser_email
```


6. Run the development server:

```shellscript
python manage.py runserver
```




### Option 2: Add to an Existing Project

1. Copy the `accounts`, `twofactor` (optional), and `core` apps to your project:

```shellscript
cp -r accounts twofactor core /path/to/your/project/
```


2. Add the apps to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'social_django',  # For social authentication
    
    # Local apps
    'accounts',
    'twofactor',  # Optional
    'core',
    
    # Your other apps
]
```


3. Configure the authentication settings (see [Configuration](#configuration) section)
4. Run migrations:

```shellscript
python manage.py makemigrations
python manage.py migrate
```




## Configuration

### Basic Settings

Add the following to your `settings.py`:

```python
# Authentication settings
AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.EmailBackend',  
    'social_core.backends.github.GithubOAuth2', # For social auth
    'social_core.backends.discord.DiscordOAuth2', # For social auth
    'social_core.backends.google.GoogleOAuth2', # For social auth
    'social_core.backends.facebook.FacebookOAuth2', # For social auth
]

# Login settings
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile'
LOGOUT_REDIRECT_URL = 'home'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'Your Site <noreply@example.com>'

# For development, you can use the console email backend
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Social Authentication settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-google-client-id'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-google-client-secret'

SOCIAL_AUTH_FACEBOOK_KEY = 'your-facebook-app-id'
SOCIAL_AUTH_FACEBOOK_SECRET = 'your-facebook-app-secret'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_GITHUB_KEY= 'your-github-client-id'
SOCIAL_AUTH_GITHUB_SECRET= 'your-github-secret-key'

SOCIAL_AUTH_DISCORD_KEY = 'your-discord-key'
SOCIAL_AUTH_DISCORD_SECRET = 'your-discord-secret'
SOCIAL_AUTH_DISCORD_SCOPE = ['identify', 'email']  
SOCIAL_AUTH_DISCORD_API_URL = 'https://discord.com/api'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'accounts.pipeline.create_user_profile',  # Custom function to create user profile
    'accounts.pipeline.set_email_verified',   # Custom function to set email as verified
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
```

### URL Configuration

Add the following to your `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('2fa/', include('twofactor.urls')),  # Optional
    path('social-auth/', include('social_django.urls', namespace='social')),
    # Your other URL patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Customization

### Templates

The authentication system uses a base template located at `templates/base.html`. You can customize this template to match your site's design.

All authentication templates are located in the following directories:

- `accounts/templates/accounts/auth/`: Login, signup, password reset, etc.
- `accounts/templates/accounts/profile/`: User profile templates
- `accounts/templates/accounts/emails/`: Email templates
- `accounts/templates/accounts/security/`: Security settings templates
- `twofactor/templates/twofactor/`: Two-factor authentication templates


To customize a template, modify the existing ones or create a new template with the same name in your project's template directory and delete the existing one.

### User Model

The authentication system uses a custom User model with email as the username field. You can extend this model by adding fields to the `UserProfile` model in `accounts/models.py`.

### Forms

All forms are located in `accounts/forms.py`. You can customize these forms by subclassing them in your project.

### Views

All views are located in `accounts/views.py`. You can customize these views by subclassing them in your project.

## Two-Factor Authentication

The Two-Factor Authentication (2FA) app is designed to be modular and can be easily added or removed from your project.

### Enabling 2FA

1. Add `'twofactor'` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'twofactor',
    # ...
]
```


2. Add the 2FA middleware to your `MIDDLEWARE` in `settings.py` right after `'django.contrib.auth.middleware.AuthenticationMiddleware'`:

```python
MIDDLEWARE = [
    # ...
    'twofactor.middleware.TwoFactorMiddleware',  # Add after authentication middleware
    # ...
]
```


3. Add the 2FA URLs to your project's `urls.py`:

```python
urlpatterns = [
    # ...
    path('2fa/', include('twofactor.urls')),
    # ...
]
```


4. Add the 2FA button to the profile template `accounts/templates/accounts/profile/profile.html`:

```html
<a href="{% url 'twofactor:security_settings' %}" class="inline-flex items-center px-4 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg text-sm font-medium text-secondary-700 dark:text-gray-300 hover:bg-secondary-50 dark:hover:bg-gray-700">
    <i class="fas fa-shield-alt mr-2"></i> Security Settings
</a>
```


5. Run migrations:

```shellscript
python manage.py makemigrations twofactor
python manage.py migrate
```




### Disabling 2FA

To disable 2FA, simply:

1. Remove `'twofactor'` from `INSTALLED_APPS`
2. Remove `'twofactor.middleware.TwoFactorMiddleware'` from `MIDDLEWARE`
3. Remove the 2FA URL pattern from your project's `urls.py`
3. Remove the 2FA button from your profile template `accounts/profile/profile.html`


No changes to the database are required, as the 2FA tables will simply be ignored when the app is not installed.

### 2FA Configuration

You can configure the following settings in your `settings.py`:

```python
# Two-Factor Authentication Settings
TWO_FACTOR_VERIFICATION_WINDOW_DAYS = 14  # Number of days before re-verification is required
TWO_FACTOR_EMAIL_OTP_EXPIRY_MINUTES = 10  # Minutes before email OTP expires
```

## Integration with Other Apps

### Social Media Platform Example

If you're building a social media platform, you can integrate the authentication system as follows:

1. Create your social media app:

```shellscript
python manage.py startapp social
```


2. Add the app to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'social',
    # ...
]
```


3. Create models that reference the User model:

```python
from django.db import models
from django.conf import settings

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Other fields...

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    # Other fields...
```


4. Create views that require authentication:

```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post

@login_required
def create_post(request):
    if request.method == 'POST':
        # Process form data
        # ...
        return redirect('social:feed')
    return render(request, 'social/create_post.html')
```


5. Add URLs for your social media app:

```python
from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('feed/', views.feed, name='feed'),
    path('post/create/', views.create_post, name='create_post'),
    # Other URLs...
]
```


6. Include your app's URLs in the project's `urls.py`:

```python
urlpatterns = [
    # ...
    path('social/', include('social.urls')),
    # ...
]
```




### E-commerce Example

For an e-commerce site:

1. Create models that reference the User model:

```python
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    # Other fields...

class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipping_addresses')
    # Other fields...
```


2. Extend the UserProfile model to include customer-specific fields:

```python
# In your app's models.py
from accounts.models import UserProfile

class CustomerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='customer_profile')
    customer_id = models.CharField(max_length=100, blank=True)
    loyalty_points = models.IntegerField(default=0)
    # Other fields...
```


3. Create a signal to create a CustomerProfile when a UserProfile is created:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import UserProfile
from .models import CustomerProfile

@receiver(post_save, sender=UserProfile)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user_profile=instance)
```




## Management Commands

### Creating a Superuser

To create a superuser with email authentication:

```shellscript
python manage.py createsuperuser_email
```

### Cleaning Up Deleted Accounts

To permanently delete accounts that were scheduled for deletion and the grace period has expired:

```shellscript
python manage.py cleanup_deleted_accounts
```

## Troubleshooting

### Common Issues

1. **Migration Issues**:

1. If you encounter migration issues, try:

```shellscript
python manage.py makemigrations
python manage.py migrate --fake-initial
```





2. **Template Not Found**:

1. Make sure your template directories are correctly configured in `settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        # ...
    },
]
```





3. **Static Files Not Loading**:

1. Make sure your static files are correctly configured in `settings.py`:

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```





4. **Email Not Sending**:

1. Check your email settings in `settings.py`
2. For development, use the console email backend or MailHog





### Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the Django documentation: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
2. Open an issue on the GitHub repository
3. Contact the maintainers at [support@example.com](mailto:support@example.com)


## File Structure

### Accounts App

```plaintext
accounts                                                                   
├─ management                                                              
│  └─ commands                                                             
│     ├─ __pycache__                                                       
│     │  └─ createsuperuser_email.cpython-313.pyc                          
│     └─ createsuperuser_email.py                                          
│     └─ cleanup_deleted_accounts.py                                        
├─ migrations                                                              
│  ├─ __pycache__                                                          
│  │  (And other related files)                                       
│  ├─ 0001_initial.py                                                      
│  └─ __init__.py                                                          
├─ templates                                                               
│  └─ accounts                                                             
│     ├─ auth                                                              
│     │  ├─ email_change.html                                              
│     │  ├─ login.html                                                     
│     │  ├─ password_change.html                                           
│     │  ├─ password_reset.html                                            
│     │  ├─ password_reset_confirm.html                                    
│     │  └─ signup.html                                                    
│     ├─ emails                                                            
│     │  ├─ activation_email.html                                          
│     │  ├─ base_email.html                                                
│     │  ├─ email_change.html                                              
│     │  ├─ login_notification.html                                        
│     │  ├─ password_change_notification.html                              
│     │  ├─ password_reset_email.html                                      
│     │  └─ welcome_email.html                                             
│     ├─ profile                                                           
│     │  ├─ edit_profile.html                                              
│     │  ├─ edit_profile_images.html                                       
│     │  └─ profile.html                                                   
│     └─ base.html                                                         
├─ __pycache__                                                             
│   (And other related files)                                     
├─ admin.py                                                                
├─ apps.py                                                                 
├─ backends.py                                                             
├─ forms.py                                                                
├─ models.py                                                               
├─ pipeline.py                                                             
├─ signals.py                                                              
├─ tests.py                                                                
├─ tokens.py                                                               
├─ urls.py                                                                 
├─ utils.py                                                                
├─ views.py                                                                
├─ widgets.py                                                              
└─ __init__.py                                                             
```

### Two-Factor Authentication App

```plaintext
twofactor                              
├─ migrations                          
│  ├─ __pycache__                      
│  │  (And other related files)
│  ├─ 0001_initial.py                  
│  └─ __init__.py                      
├─ templates                           
│  └─ twofactor                        
│     ├─ emails                        
│     │  ├─ base_email.html            
│     │  └─ otp_email.html             
│     ├─ backup_codes.html             
│     ├─ base_2fa.html                 
│     ├─ change_2fa_method.html        
│     ├─ disable_2fa.html              
│     ├─ security_settings.html        
│     ├─ setup_2fa.html                
│     ├─ setup_totp.html               
│     ├─ verify_2fa.html               
│     └─ verify_email_otp.html         
├─ __pycache__                         
│  (And other related files)        
├─ admin.py                            
├─ apps.py                             
├─ forms.py                            
├─ middleware.py                       
├─ models.py                           
├─ signals.py                          
├─ tests.py                            
├─ urls.py                             
├─ utils.py                            
├─ views.py                            
└─ __init__.py                         
```

### Core App

```plaintext
core                                      
├─ migrations                             
│  ├─ __pycache__                         
│  (And other related files)
│  ├─ 0001_initial.py                     
│  └─ __init__.py                         
├─ templates                              
│  ├─ core/                                
│  ├─ base.html                           
│  └─ home.html                           
├─ __pycache__                            
│  (And other related files)
├─ admin.py                               
├─ apps.py                                
├─ context_processors.py                  
├─ models.py                              
├─ tests.py                               
├─ urls.py                                
├─ views.py                               
└─ __init__.py
```

```

This completes the setup guide for the Django Authentication System. For more information, please refer to the documentation or contact the maintainers.