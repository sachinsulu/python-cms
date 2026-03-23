# articles/models.py
from django.db import models, transaction
from django.db.models import Max
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField


class Article(models.Model):
    title    = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    slug     = models.SlugField(unique=True, blank=True)

    # ── Legacy ImageField (kept during transition — DO NOT REMOVE YET) ──
    # Renamed from the original 'image' to free up the field name for the FK.
    # Remove this in a future cleanup migration after all data is backfilled.
    image_legacy = models.ImageField(
        upload_to='articles/',
        blank=True,
        null=True,
        verbose_name='[Legacy] Image',
    )

    # ── New FK field ─────────────────────────────────────────────────────
    image = models.ForeignKey(
        'media_manager.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='article_images',
        verbose_name='Image',
    )

    content  = RichTextUploadingField(blank=False)
    homepage = models.BooleanField(default=False)
    active   = models.BooleanField(default=True)

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    position   = models.PositiveIntegerField(default=0)

    meta_title       = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords    = models.CharField(max_length=205, blank=True)

    class Meta:
        ordering = ['position']

    # ── Image URL resolver ────────────────────────────────────────────────
    @property
    def image_url(self):
        """
        FK takes priority over legacy.
        Returns None if neither is set.
        Templates should always use article.image_url — never article.image directly.
        """
        if self.image_id:
            try:
                return self.image.file.url
            except (ValueError, AttributeError):
                pass
        if self.image_legacy:
            try:
                return self.image_legacy.url
            except (ValueError, AttributeError):
                pass
        return None

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.id or self.position == 0:
                last_pos = Article.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last_pos or 0) + 1

            if not self.slug:
                from cms.utils import is_slug_taken
                base_slug = slugify(self.title, allow_unicode=True)
                slug = base_slug
                counter = 1
                while is_slug_taken(slug, exclude_obj=self):
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug

            super().save(*args, **kwargs)

    def __str__(self):
        return self.title