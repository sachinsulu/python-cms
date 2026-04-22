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

    MEDIA_TYPE_IMAGE = 'image'
    MEDIA_TYPE_VIDEO = 'video'
    MEDIA_TYPE_CHOICES = [
        (MEDIA_TYPE_IMAGE, 'Image'),
        (MEDIA_TYPE_VIDEO, 'Video'),
    ]

    title = models.CharField(max_length=255)
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_INNERPAGE
    )
    media_type = models.CharField(
        max_length=10, choices=MEDIA_TYPE_CHOICES, default=MEDIA_TYPE_IMAGE
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
    youtube_url = models.URLField(max_length=500, blank=True, default='')
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, default='')
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

    @property
    def media_type(self):
        """Return media type: 'image', 'video', or None."""
        if self.image_id:
            try:
                return self.image.type
            except (ValueError, AttributeError):
                pass
        return None

    @property
    def is_youtube(self):
        """Return True if this item is a YouTube link (not an uploaded file)."""
        return bool(self.youtube_url)

    @property
    def youtube_embed_url(self):
        """Return the YouTube embed URL extracted from youtube_url, or None."""
        import re
        if not self.youtube_url:
            return None
        # Robust regex for various YouTube URL formats
        pattern = r'(?:v=|v\/|youtu\.be\/|embed\/|shorts\/|^)([\w-]{11})(?![^\w-])'
        m = re.search(pattern, self.youtube_url)
        if m:
            return f'https://www.youtube.com/embed/{m.group(1)}'
        return None

    @property
    def youtube_thumbnail_url(self):
        """Return YouTube thumbnail URL, or None."""
        import re
        if not self.youtube_url:
            return None
        pattern = r'(?:v=|v\/|youtu\.be\/|embed\/|shorts\/|^)([\w-]{11})(?![^\w-])'
        m = re.search(pattern, self.youtube_url)
        if m:
            return f'https://img.youtube.com/vi/{m.group(1)}/mqdefault.jpg'
        return None

    @property
    def is_video(self):
        """Return True if media is a video (uploaded file or YouTube)."""
        return self.media_type == 'video' or self.is_youtube

    @property
    def media_url(self):
        """Return media file URL (same as image_url for compatibility)."""
        return self.image_url

    @property
    def thumbnail_or_poster_url(self):
        """Return thumbnail for images, or file URL for videos."""
        if self.is_video:
            return self.image_url
        return self.thumbnail_url or self.image_url

    def __str__(self):
        return self.title or f"Image for {self.gallery.title}"
