from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_account_view, name='activate'),
    path('verify-email-change/<uidb64>/<token>/', views.verify_email_change_view, name='verify_email_change'),
    
    # Password management
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password-change/', views.password_change_view, name='password_change'),
    
    # Profile management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_update_view, name='profile_edit'),
    path('profile/edit/images/', views.profile_images_update_view, name='profile_edit_images'),
    path('email/change/', views.email_change_view, name='email_change'),
]