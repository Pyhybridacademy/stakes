from .models import SiteSettings, StaticPage

def site_settings(request):
    site_settings = SiteSettings.load()
    static_pages = StaticPage.objects.filter(is_active=True).first()
    
    return {
        'site_settings': site_settings,
        'static_pages': static_pages,
    }