import os
from django.utils import timezone
from preferences.models import SitePreferences
from location.models import Location
from social.models import Social
from menu.models import MenuItem

def frontend_context(request):
    try:
        site_prefs = SitePreferences.objects.get_solo()
    except Exception:
        site_prefs = None

    if site_prefs and site_prefs.copyright_text:
        site_prefs.copyright_text = site_prefs.copyright_text.replace('{year}', str(timezone.now().year))

    try:
        site_location = Location.objects.get_solo()
    except Exception:
        site_location = None

    # ✅ Extract first phone number
    primary_phone = None
    if site_location and site_location.phone:
        from core.phone_utils import split_and_normalize_phones, normalize_phone
        first_phone = split_and_normalize_phones(site_location.phone)[0]
        # Clean for WhatsApp link (digits only)
        import re
        primary_phone = re.sub(r'[^\d+]', '', first_phone)

    social_links = Social.objects.filter(active=True, type=Social.TYPE_SOCIAL).order_by('position')
    ota_links = Social.objects.filter(active=True, type=Social.TYPE_OTA).order_by('position')
    
    main_menu = MenuItem.objects.filter(active=True, parent=None).order_by('position').prefetch_related('children')

    return {
        'site_prefs': site_prefs,
        'site_location': site_location,
        'primary_phone': primary_phone,  # 👈 NEW
        'social_links': social_links,
        'ota_links': ota_links,
        'main_menu': main_menu,
        'RECAPTCHA_SITE_KEY': os.environ.get("RECAPTCHA_SITE_KEY"),
    }
