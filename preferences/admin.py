from django.contrib import admin
from django.utils.html import format_html
from .models import SitePreferences


@admin.register(SitePreferences)
class SitePreferencesAdmin(admin.ModelAdmin):
    """
    Admin for the SitePreferences singleton.
    - The "Add" button is hidden once the single instance exists.
    - Fieldsets group related settings for clarity.
    - Thumbnail previews are shown alongside each ImageField.
    """

    readonly_fields = (
        'updated_at',
        # Image preview helpers
        'icon_preview',
        'logo_preview',
        'fb_sharing_preview',
        'twitter_sharing_preview',
        'gallery_image_preview',
        'contact_image_preview',
        'default_image_preview',
        'facilities_image_preview',
        'offer_image_preview',
    )

    fieldsets = (
        ('🔴 Site Status', {
            'fields': ('is_maintenance',),
            'description': (
                'Toggle maintenance mode. The API still serves data; '
                'the frontend is responsible for gating on this flag.'
            ),
        }),
        ('🏷️ Identity', {
            'fields': ('site_title', 'site_name', 'copyright_text'),
        }),
        ('🖼️ Media — Branding', {
            'fields': (
                'icon',        'icon_preview',
                'logo',        'logo_preview',
            ),
        }),
        ('🖼️ Media — Social Sharing', {
            'fields': (
                'fb_sharing',      'fb_sharing_preview',
                'twitter_sharing', 'twitter_sharing_preview',
            ),
        }),
        ('🖼️ Media — Pages', {
            'fields': (
                'gallery_image',    'gallery_image_preview',
                'contact_image',    'contact_image_preview',
                'default_image',    'default_image_preview',
                'facilities_image', 'facilities_image_preview',
                'offer_image',      'offer_image_preview',
            ),
        }),
        ('📜 Tracking Scripts', {
            'classes': ('collapse',),
            'description': '⚠️ These fields accept raw HTML/JS. Only superusers should edit them.',
            'fields': (
                'google_analytics_code',
                'facebook_pixel_code',
                'online_booking_code',
            ),
        }),
        ('🤖 SEO', {
            'classes': ('collapse',),
            'fields': ('robots_txt',),
            'description': 'Content served at /robots.txt. Leave blank for a permissive default.',
        }),
        ('🏨 Booking Configuration', {
            'fields': ('booking_type', 'hotel_result_page', 'hotel_code'),
        }),
        ('ℹ️ Meta', {
            'fields': ('updated_at',),
        }),
    )

    # ── Singleton guards ───────────────────────────────────────────────────

    def has_add_permission(self, request):
        """Disable the Add button once the singleton instance exists."""
        return not SitePreferences.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Never allow deletion from the admin."""
        return False

    # ── Image preview helpers ──────────────────────────────────────────────

    def _preview(self, image_field, label=''):
        if image_field:
            return format_html(
                '<img src="{}" style="max-height:80px; max-width:200px; '
                'object-fit:contain; border:1px solid #e5e7eb; border-radius:4px;" '
                'alt="{}">',
                image_field.url,
                label,
            )
        return '—'

    def icon_preview(self, obj):
        return self._preview(obj.icon, 'Icon')
    icon_preview.short_description = 'Preview'

    def logo_preview(self, obj):
        return self._preview(obj.logo, 'Logo')
    logo_preview.short_description = 'Preview'

    def fb_sharing_preview(self, obj):
        return self._preview(obj.fb_sharing, 'FB Sharing')
    fb_sharing_preview.short_description = 'Preview'

    def twitter_sharing_preview(self, obj):
        return self._preview(obj.twitter_sharing, 'Twitter Sharing')
    twitter_sharing_preview.short_description = 'Preview'

    def gallery_image_preview(self, obj):
        return self._preview(obj.gallery_image, 'Gallery')
    gallery_image_preview.short_description = 'Preview'

    def contact_image_preview(self, obj):
        return self._preview(obj.contact_image, 'Contact')
    contact_image_preview.short_description = 'Preview'

    def default_image_preview(self, obj):
        return self._preview(obj.default_image, 'Default')
    default_image_preview.short_description = 'Preview'

    def facilities_image_preview(self, obj):
        return self._preview(obj.facilities_image, 'Facilities')
    facilities_image_preview.short_description = 'Preview'

    def offer_image_preview(self, obj):
        return self._preview(obj.offer_image, 'Offer')
    offer_image_preview.short_description = 'Preview'