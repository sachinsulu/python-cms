from django.db import models, transaction
from django.db.models import Max
from django.utils.text import slugify
from media_manager.mixins import MediaUsageMixin

class Gallery(models.Model):
    TYPE_HOMEPAGE = 'Homepage'
    TYPE_INNERPAGE = 'Innerpage'
    TYPE_CHOICES = [
        (TYPE_HOMEPAGE, 'Homepage'),
        (TYPE_INNERPAGE, 'Innerpage'),
    ]

    title = models.CharField(max_length=255)
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_INNERPAGE
    )
    active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.id:
                last_pos = Gallery.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last_pos or 0) + 1

            super().save(*args, **kwargs)


class GalleryImage(MediaUsageMixin, models.Model):
    media_fields = ['image']
    
    gallery = models.ForeignKey(
        Gallery, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ForeignKey(
        'media_manager.Media', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL, 
        related_name='gallery_images'
    )
    title = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']

    @property
    def image_url(self):
        """Return the file URL of the linked Media object, or None."""
        try:
            return self.image.file.url if self.image_id else None
        except (ValueError, AttributeError):
            return None

    @property
    def thumbnail_url(self):
        """Return the thumbnail URL of the linked Media object, or None."""
        try:
            return self.image.thumbnail_url if self.image_id else None
        except (ValueError, AttributeError):
            return None

    def __str__(self):
        return self.title or f"Image for {self.gallery.title}"
