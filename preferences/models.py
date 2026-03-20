from django.db import models
from django.core.cache import cache


PREFS_CACHE_KEY = 'site_preferences_singleton'


class SitePreferencesManager(models.Manager):
    def get_solo(self):
        """
        Always returns the single SitePreferences instance.
        Creates it with pk=1 if it does not yet exist.
        Result is cached to avoid a DB hit on every request.
        """
        obj = cache.get(PREFS_CACHE_KEY)
        if obj is None:
            obj, _ = self.get_or_create(pk=1)
            cache.set(PREFS_CACHE_KEY, obj, timeout=None)  # indefinite — invalidated on save
        return obj


class BookingType(models.TextChoices):
    DEFAULT = 'default', 'Default'
    ROJAI   = 'rojai',   'Rojai'


class SitePreferences(models.Model):
    """
    Singleton model — only one row (pk=1) is ever allowed.
    Stores global site identity, media assets, tracking scripts,
    SEO configuration, and booking integration settings.
    """

    # ── Status ────────────────────────────────────────────────────────────
    is_maintenance = models.BooleanField(
        default=False,
        verbose_name='Maintenance / Under Construction',
        help_text='When enabled, the frontend should display a maintenance page.',
    )

    # ── Identity ──────────────────────────────────────────────────────────
    site_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name='Site Title',
        help_text='Used in <title> tags. Max 60 characters.',
    )
    site_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Site Name',
        help_text='Short brand name shown in the UI.',
    )
    copyright_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Copyright Text',
        help_text='e.g. © 2025 My Hotel. All rights reserved.',
    )

    # ── Media ─────────────────────────────────────────────────────────────
    icon = models.ImageField(
        upload_to='prefs/identity/',
        blank=True, null=True,
        verbose_name='Favicon / Icon',
    )
    logo = models.ImageField(
        upload_to='prefs/identity/',
        blank=True, null=True,
        verbose_name='Logo',
    )
    fb_sharing = models.ImageField(
        upload_to='prefs/social/',
        blank=True, null=True,
        verbose_name='Facebook Sharing Image',
        help_text='Recommended: 1200×630px.',
    )
    twitter_sharing = models.ImageField(
        upload_to='prefs/social/',
        blank=True, null=True,
        verbose_name='Twitter / X Sharing Image',
        help_text='Recommended: 1200×600px.',
    )
    gallery_image = models.ImageField(
        upload_to='prefs/pages/',
        blank=True, null=True,
        verbose_name='Gallery Page Image',
    )
    contact_image = models.ImageField(
        upload_to='prefs/pages/',
        blank=True, null=True,
        verbose_name='Contact Page Image',
    )
    default_image = models.ImageField(
        upload_to='prefs/pages/',
        blank=True, null=True,
        verbose_name='Default / Fallback Image',
        help_text='Used when a specific image is not set.',
    )
    facilities_image = models.ImageField(
        upload_to='prefs/pages/',
        blank=True, null=True,
        verbose_name='Facilities Page Image',
    )
    offer_image = models.ImageField(
        upload_to='prefs/pages/',
        blank=True, null=True,
        verbose_name='Offer Page Image',
    )

    # ── Scripts ───────────────────────────────────────────────────────────
    google_analytics_code = models.TextField(
        blank=True,
        verbose_name='Google Analytics Code',
        help_text='Paste the full <script> tag or measurement ID. Raw HTML — admin only.',
    )
    facebook_pixel_code = models.TextField(
        blank=True,
        verbose_name='Facebook Pixel Code',
        help_text='Paste the full Facebook Pixel <script> block. Raw HTML — admin only.',
    )
    online_booking_code = models.TextField(
        blank=True,
        verbose_name='Online Booking Embed Code',
        help_text='Third-party booking widget embed code. Raw HTML — admin only.',
    )

    # ── SEO ───────────────────────────────────────────────────────────────
    robots_txt = models.TextField(
        blank=True,
        verbose_name='robots.txt Content',
        help_text='Full content of /robots.txt. Leave blank to serve a permissive default.',
    )

    # ── Booking ───────────────────────────────────────────────────────────
    booking_type = models.CharField(
        max_length=20,
        choices=BookingType.choices,
        default=BookingType.DEFAULT,
        verbose_name='Booking Engine Type',
    )
    hotel_result_page = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Hotel Result Page URL',
        help_text='URL of the results page used by the booking engine.',
    )
    hotel_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Hotel Code',
        help_text='Property identifier for the booking engine.',
    )

    # ── Timestamps ────────────────────────────────────────────────────────
    updated_at = models.DateTimeField(auto_now=True)

    objects = SitePreferencesManager()

    class Meta:
        verbose_name         = 'Site Preferences'
        verbose_name_plural  = 'Site Preferences'

    # ── Singleton enforcement ─────────────────────────────────────────────

    def save(self, *args, **kwargs):
        """Force pk=1 so only one row ever exists, then bust the cache."""
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(PREFS_CACHE_KEY)

    def delete(self, *args, **kwargs):
        """Prevent deletion — the singleton row must always exist."""
        raise PermissionError(
            'SitePreferences is a singleton and cannot be deleted. '
            'Reset individual fields to their defaults instead.'
        )

    def __str__(self):
        return 'Site Preferences'