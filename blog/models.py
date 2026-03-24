# blog/models.py
from django.db import models, transaction
from django.utils.text import slugify
from django.db.models import Max
from ckeditor_uploader.fields import RichTextUploadingField

from media_manager.mixins import MediaUsageMixin


class Blog(MediaUsageMixin, models.Model):
    media_fields = ['banner_image', 'image']
    title  = models.CharField(max_length=255)
    slug   = models.SlugField(unique=True, blank=True)
    author = models.CharField(max_length=255, blank=True)
    date   = models.DateField(null=True, blank=True)


    # ── New FK fields ──────────────────────────────────────────────
    banner_image = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_banner_images',
        verbose_name='Banner Image',
    )
    image = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_images',
        verbose_name='Image',
    )

    content  = RichTextUploadingField(blank=True)
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta_title       = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords    = models.CharField(max_length=205, blank=True)

    class Meta:
        ordering = ['position']

    @property
    def image_url(self):
        if self.image_id:
            try:
                return self.image.file.url
            except (ValueError, AttributeError):
                pass
        return None

    @property
    def banner_image_url(self):
        if self.banner_image_id:
            try:
                return self.banner_image.file.url
            except (ValueError, AttributeError):
                pass
        return None

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.id or self.position == 0:
                last_pos = Blog.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last_pos or 0) + 1

            if not self.slug:
                from cms.utils import is_slug_taken
                base_slug = slugify(self.title, allow_unicode=True)
                slug      = base_slug
                counter   = 1
                while is_slug_taken(slug, exclude_obj=self):
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug

            super().save(*args, **kwargs)

    def __str__(self):
        return self.title