from decouple import config, Csv
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-n9980oha*#u&tm6!!w%1po8rgi1v63i8_an#2tgh3mrg7zo0s+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'stakes-pn8o.onrender.com'] 


# Application definition

INSTALLED_APPS = [
    'django_admin_kubi',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'django_cleanup.apps.CleanupConfig',
    'django_ckeditor_5',
    'social_django',

    # Custom apps
    'accounts',
    'twofactor',
    'core',
    'staking',
    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'twofactor.middleware.TwoFactorMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'django_auth_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_auth_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files settings
MEDIA_URL = '/media/'  # URL to access media files in templates
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Directory to store uploaded media files

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --------------------------------------------------
# Custom settings for the project
# --------------------------------------------------

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.EmailBackend',  
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.discord.DiscordOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
]

# # Email Settings (Development - MailHog)
# EMAIL_BACKEND= 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST= 'localhost'
# EMAIL_PORT= 1025
# EMAIL_USE_TLS= False
# EMAIL_HOST_USER= ''
# EMAIL_HOST_PASSWORD= ''
# DEFAULT_FROM_EMAIL= 'noreply@example.com'


# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_TRUSTED_ORIGINS = ['https://stakes-pn8o.onrender.com'

# Login settings
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'staking:dashboard'
LOGOUT_REDIRECT_URL = 'home'


# Social Authentication
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY= 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET= 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'

SOCIAL_AUTH_FACEBOOK_KEY= 'SOCIAL_AUTH_FACEBOOK_KEY'
SOCIAL_AUTH_FACEBOOK_SECRET= 'SOCIAL_AUTH_FACEBOOK_SECRET'
SOCIAL_AUTH_FACEBOOK_SCOPE= ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS= {'fields': 'id,name,email'}

SOCIAL_AUTH_GITHUB_KEY= 'SOCIAL_AUTH_GITHUB_KEY'
SOCIAL_AUTH_GITHUB_SECRET= 'SOCIAL_AUTH_GITHUB_SECRET'
SOCIAL_AUTH_GITHUB_SCOPE= ['user:email']

SOCIAL_AUTH_DISCORD_KEY = 'SOCIAL_AUTH_DISCORD_KEY'
SOCIAL_AUTH_DISCORD_SECRET = 'SOCIAL_AUTH_DISCORD_SECRET'
SOCIAL_AUTH_DISCORD_SCOPE = ['identify', 'email']  
SOCIAL_AUTH_DISCORD_API_URL = 'https://discord.com/api'

# General social auth settings
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'home'
SOCIAL_AUTH_LOGIN_ERROR_URL = 'accounts:login'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = 'accounts:profile'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = 'accounts:profile'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = 'accounts:login'

# User model settings
SOCIAL_AUTH_USER_MODEL = 'accounts.User'

# Pipeline to create user profiles and handle email verification
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


# Two-factor authentication settings
TWO_FACTOR_VERIFICATION_WINDOW_DAYS = 14  # Number of days before re-verification is required
TWO_FACTOR_EMAIL_OTP_EXPIRY_MINUTES = 10  # Minutes before email OTP expires
# TWO_FACTOR_CALL_GATEWAY = None  # Disable call gateway
# TWO_FACTOR_SMS_GATEWAY = None   # Disable SMS gateway (you can enable later with a provider)

# Django flash message storage in cookies
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


# Django CKEditor settings

# Optional: Restrict the formats of the uploaded images
CKEDITOR_IMAGE_BACKEND = "pillow"  # or "pil"

# Optional: Thumbnail size
CKEDITOR_THUMBNAIL_SIZE = (300, 300)

# Optional: Custom CKEditor settings
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage',  # Include the upload image plugin
            # other extra plugins you want to add
        ]),
    },
}

# CKEditor Configuration

customColorPalette = [
        {
            'color': 'hsl(4, 90%, 58%)',
            'label': 'Red'
        },
        {
            'color': 'hsl(340, 82%, 52%)',
            'label': 'Pink'
        },
        {
            'color': 'hsl(291, 64%, 42%)',
            'label': 'Purple'
        },
        {
            'color': 'hsl(262, 52%, 47%)',
            'label': 'Deep Purple'
        },
        {
            'color': 'hsl(231, 48%, 48%)',
            'label': 'Indigo'
        },
        {
            'color': 'hsl(207, 90%, 54%)',
            'label': 'Blue'
        },
    ]

CKEDITOR_5_CUSTOM_CSS = 'css/ckeditor.css' 
CKEDITOR_5_UPLOAD_PATH = "posts/post_images/" 
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': [
                'heading', 'fontFamily', 'fontSize', 'fontColor', 'fontBackgroundColor',
                '|',
                'bold', 'italic', 'underline', 'strikethrough', 'subscript', 'superscript',
                '|',
                'alignment', 'bulletedList', 'numberedList', 'todoList',
                '|',
                'link', 'insertImage', 'imageUpload', 'mediaEmbed',
                '|',
                'code', 'codeBlock', 'sourceEditing', 'highlight',
                '|',
                'outdent', 'indent', 'blockQuote', 'horizontalLine', 'removeFormat',
                '|',
                'undo', 'redo', 'findAndReplace', 'insertTable', 'specialCharacters'
                
            ],
            'extraPlugins': 'GeneralHtmlSupport',
            'htmlSupport': {
                'allow': [
                    {
                        'name': '.*',
                        'attributes': True,
                        'classes': True,
                        'styles': True
                    }
                ],
            },
            'shouldNotGroupWhenFull': True
        },
        'menuBar': {
            'isVisible': True
        },
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': 'customColorPalette',
                'backgroundColors': 'customColorPalette'
            },
            'tableCellProperties': {
                'borderColors': 'customColorPalette',
                'backgroundColors': 'customColorPalette'
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
                {'model': 'heading5', 'view': 'h5', 'title': 'Heading 5', 'class': 'ck-heading_heading5'},
                {'model': 'heading6', 'view': 'h6', 'title': 'Heading 6', 'class': 'ck-heading_heading6'}
            ]
        },
        'mention': {
            'feeds': [
                {
                    'marker': '@',
                    'feed': ['@John', '@Jane', '@Admin'],
                    'minimumCharacters': 1
                }
            ]
        },
        'upload': {
            "types": ['png', 'jpg', 'jpeg', 'gif']
        },
        
        
    }
}
