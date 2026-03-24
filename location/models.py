from django.db import models
from django.core.cache import cache
from ckeditor_uploader.fields import RichTextUploadingField

LOCATION_CACHE_KEY = 'location_singleton'


class LocationManager(models.Manager):
    def get_solo(self):
        obj = cache.get(LOCATION_CACHE_KEY)
        if obj is None:
            obj, _ = self.get_or_create(pk=1)
            cache.set(LOCATION_CACHE_KEY, obj, timeout=None)
        return obj


class Location(models.Model):
    fiscal_address   = models.TextField(blank=True)
    ktm_address      = models.TextField(blank=True)
    ktm_contact_info = models.CharField(max_length=255, blank=True)
    ktm_email        = models.EmailField(blank=True)
    landline         = models.CharField(max_length=50, blank=True)
    phone            = models.CharField(max_length=50, blank=True)
    p_o_box          = models.CharField(max_length=100, blank=True)
    email_address    = models.EmailField(blank=True)
    whatsapp         = models.CharField(max_length=50, blank=True)
    map_embed        = models.TextField(
        blank=True,
        help_text='Paste Google Maps <iframe> embed code or a plain URL.'
    )
    content          = RichTextUploadingField(blank=True)
    updated_at       = models.DateTimeField(auto_now=True)

    objects = LocationManager()

    class Meta:
        verbose_name        = 'Location'
        verbose_name_plural = 'Location'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(LOCATION_CACHE_KEY)

    def delete(self, *args, **kwargs):
        raise PermissionError(
            'Location is a singleton and cannot be deleted.'
        )

    def __str__(self):
        return 'Location Settings'
