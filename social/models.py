from django.db import models
from django.db import transaction
from django.db.models import Max

from media_manager.mixins import MediaUsageMixin


class Social(MediaUsageMixin, models.Model):
    media_fields = ['image']
    TYPE_SOCIAL = 'social'
    TYPE_OTA    = 'ota'
    TYPE_CHOICES = [
        (TYPE_SOCIAL, 'Social'),
        (TYPE_OTA,    'OTA'),
    ]

    title    = models.CharField(max_length=255)

    # Kept as CharField — URLField would be a breaking ALTER TABLE
    # and existing data may contain relative paths.
    # URL validation is enforced at the form layer instead.
    link     = models.CharField(max_length=500, blank=True)

    icon     = models.CharField(
        max_length=255, blank=True,
        help_text='CSS class e.g. fa-brands fa-instagram',
    )
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    type     = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=TYPE_SOCIAL,
    )



    # New FK field
    image = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='social_entries',
        verbose_name='Image',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['position']
        verbose_name        = 'Social / OTA'
        verbose_name_plural = 'Socials / OTAs'

    @property
    def image_url(self):
        if self.image_id:
            try:
                return self.image.file.url
            except (ValueError, AttributeError):
                pass
        return None

    @property
    def thumbnail_url(self):
        if self.image_id:
            try:
                return self.image.thumbnail_url
            except (ValueError, AttributeError):
                pass
        return None

    def __str__(self):
        return self.title