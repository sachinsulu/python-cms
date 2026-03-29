from preferences.models import SitePreferences
from location.models import Location
from social.models import Social
from menu.models import MenuItem

def frontend_context(request):
    """
    Context processor to provide global site data (branding, contact info, social links)
    to all frontend templates.
    """
    try:
        site_prefs = SitePreferences.objects.get_solo()
    except Exception:
        site_prefs = None

    try:
        site_location = Location.objects.get_solo()
    except Exception:
        site_location = None

    social_links = Social.objects.filter(active=True, type=Social.TYPE_SOCIAL)
    ota_links = Social.objects.filter(active=True, type=Social.TYPE_OTA)
    
    # Top-level menu items only
    main_menu = MenuItem.objects.filter(active=True, parent=None).prefetch_related('children')

    return {
        'site_prefs': site_prefs,
        'site_location': site_location,
        'social_links': social_links,
        'ota_links': ota_links,
        'main_menu': main_menu,
    }
