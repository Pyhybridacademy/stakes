from django.contrib import admin
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from .models import SiteSettings, StaticPage


admin.site.register(SiteSettings)

admin.site.register(StaticPage)
