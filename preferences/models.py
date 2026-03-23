from django.db import models
from django.core.cache import cache

PREFS_CACHE_KEY = 'site_preferences_singleton'


class SitePreferencesManager(models.Manager):
    def get_solo(self):
        obj = cache.get(PREFS_CACHE_KEY)
        if obj is None:
            obj, _ = self.get_or_create(pk=1)
            cache.set(PREFS_CACHE_KEY, obj, timeout=None)
        return obj


class BookingType(models.TextChoices):
    DEFAULT = 'default', 'Default'
    ROJAI   = 'rojai',   'Rojai'


class SitePreferences(models.Model):

    # ── Status ────────────────────────────────────────────────────────────
    is_maintenance = models.BooleanField(
        default=False,
        verbose_name='Maintenance / Under Construction',
        help_text='When enabled, the frontend should display a maintenance page.',
    )

    # ── Identity ──────────────────────────────────────────────────────────
    site_title = models.CharField(
        max_length=60, blank=True, verbose_name='Site Title',
        help_text='Used in <title> tags. Max 60 characters.',
    )
    site_name = models.CharField(
        max_length=100, blank=True, verbose_name='Site Name',
        help_text='Short brand name shown in the UI.',
    )
    copyright_text = models.CharField(
        max_length=255, blank=True, verbose_name='Copyright Text',
        help_text='e.g. © 2025 My Hotel. All rights reserved.',
    )

    # ── Legacy ImageFields (kept during transition — DO NOT REMOVE YET) ───
    # These are renamed from the originals to free up the field names for FKs.
    # Remove these in Phase 3b, after MediaUsage tracking is in place.
    icon_legacy             = models.ImageField(upload_to='prefs/identity/', blank=True, null=True, verbose_name='[Legacy] Icon')
    logo_legacy             = models.ImageField(upload_to='prefs/identity/', blank=True, null=True, verbose_name='[Legacy] Logo')
    fb_sharing_legacy       = models.ImageField(upload_to='prefs/social/',   blank=True, null=True, verbose_name='[Legacy] FB Sharing')
    twitter_sharing_legacy  = models.ImageField(upload_to='prefs/social/',   blank=True, null=True, verbose_name='[Legacy] Twitter Sharing')
    gallery_image_legacy    = models.ImageField(upload_to='prefs/pages/',    blank=True, null=True, verbose_name='[Legacy] Gallery Image')
    contact_image_legacy    = models.ImageField(upload_to='prefs/pages/',    blank=True, null=True, verbose_name='[Legacy] Contact Image')
    default_image_legacy    = models.ImageField(upload_to='prefs/pages/',    blank=True, null=True, verbose_name='[Legacy] Default Image')
    facilities_image_legacy = models.ImageField(upload_to='prefs/pages/',    blank=True, null=True, verbose_name='[Legacy] Facilities Image')
    offer_image_legacy      = models.ImageField(upload_to='prefs/pages/',    blank=True, null=True, verbose_name='[Legacy] Offer Image')

    # ── New FK fields (nullable during transition) ────────────────────────
    icon = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_icon',
        verbose_name='Icon',
    )
    logo = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_logo',
        verbose_name='Logo',
    )
    fb_sharing = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_fb_sharing',
        verbose_name='Facebook Sharing Image',
        help_text='Recommended: 1200×630px.',
    )
    twitter_sharing = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_twitter_sharing',
        verbose_name='Twitter / X Sharing Image',
        help_text='Recommended: 1200×600px.',
    )
    gallery_image = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_gallery',
        verbose_name='Gallery Page Image',
    )
    contact_image = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_contact',
        verbose_name='Contact Page Image',
    )
    default_image = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_default',
        verbose_name='Default / Fallback Image',
        help_text='Used when a specific image is not set.',
    )
    facilities_image = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_facilities',
        verbose_name='Facilities Page Image',
    )
    offer_image = models.ForeignKey(
        'media_manager.Media', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='prefs_offer',
        verbose_name='Offer Page Image',
    )

    # ── Scripts ───────────────────────────────────────────────────────────
    google_analytics_code = models.TextField(
        blank=True, verbose_name='Google Analytics Code',
        help_text='Paste the full <script> tag or measurement ID. Raw HTML — admin only.',
    )
    facebook_pixel_code = models.TextField(
        blank=True, verbose_name='Facebook Pixel Code',
        help_text='Paste the full Facebook Pixel <script> block. Raw HTML — admin only.',
    )
    online_booking_code = models.TextField(
        blank=True, verbose_name='Online Booking Embed Code',
        help_text='Third-party booking widget embed code. Raw HTML — admin only.',
    )

    # ── SEO ───────────────────────────────────────────────────────────────
    robots_txt = models.TextField(
        blank=True, verbose_name='robots.txt Content',
        help_text='Full content of /robots.txt. Leave blank to serve a permissive default.',
    )

    # ── Booking ───────────────────────────────────────────────────────────
    booking_type = models.CharField(
        max_length=20, choices=BookingType.choices, default=BookingType.DEFAULT,
        verbose_name='Booking Engine Type',
    )
    hotel_result_page = models.CharField(
        max_length=255, blank=True, verbose_name='Hotel Result Page URL',
        help_text='URL of the results page used by the booking engine.',
    )
    hotel_code = models.CharField(
        max_length=100, blank=True, verbose_name='Hotel Code',
        help_text='Property identifier for the booking engine.',
    )

    # ── Timestamps ────────────────────────────────────────────────────────
    updated_at = models.DateTimeField(auto_now=True)

    objects = SitePreferencesManager()

    class Meta:
        verbose_name        = 'Site Preferences'
        verbose_name_plural = 'Site Preferences'

    # ── URL resolver properties ───────────────────────────────────────────
    # FK takes priority over legacy. Templates use these exclusively.
    # Never access .icon.file.url directly in templates — use .icon_url.

    def _resolve_url(self, fk_id, fk_obj, legacy_field):
        """
        Use the _id sentinel to check presence — avoids AttributeError
        on deferred/null FK objects.
        """
        if fk_id:
            try:
                return fk_obj.file.url
            except (ValueError, AttributeError):
                pass
        if legacy_field:
            try:
                return legacy_field.url
            except (ValueError, AttributeError):
                pass
        return None

    @property
    def icon_url(self):
        return self._resolve_url(self.icon_id, self.icon, self.icon_legacy)

    @property
    def logo_url(self):
        return self._resolve_url(self.logo_id, self.logo, self.logo_legacy)

    @property
    def fb_sharing_url(self):
        return self._resolve_url(self.fb_sharing_id, self.fb_sharing, self.fb_sharing_legacy)

    @property
    def twitter_sharing_url(self):
        return self._resolve_url(self.twitter_sharing_id, self.twitter_sharing, self.twitter_sharing_legacy)

    @property
    def gallery_image_url(self):
        return self._resolve_url(self.gallery_image_id, self.gallery_image, self.gallery_image_legacy)

    @property
    def contact_image_url(self):
        return self._resolve_url(self.contact_image_id, self.contact_image, self.contact_image_legacy)

    @property
    def default_image_url(self):
        return self._resolve_url(self.default_image_id, self.default_image, self.default_image_legacy)

    @property
    def facilities_image_url(self):
        return self._resolve_url(self.facilities_image_id, self.facilities_image, self.facilities_image_legacy)

    @property
    def offer_image_url(self):
        return self._resolve_url(self.offer_image_id, self.offer_image, self.offer_image_legacy)

    # ── Singleton enforcement ─────────────────────────────────────────────
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(PREFS_CACHE_KEY)

    def delete(self, *args, **kwargs):
        raise PermissionError(
            'SitePreferences is a singleton and cannot be deleted. '
            'Reset individual fields to their defaults instead.'
        )

    def __str__(self):
        return 'Site Preferences'