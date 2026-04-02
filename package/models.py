from django.db import models, transaction
from django.utils.text import slugify
from django.db.models import Max
from ckeditor_uploader.fields import RichTextUploadingField

from media_manager.mixins import MediaUsageMixin


class Package(MediaUsageMixin, models.Model):
    media_fields = ['image']
    PACKAGE_TYPE_CHOICES = [
        ('room', 'Room'),
        ('non_room', 'Non-Room'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = RichTextUploadingField(blank=True)


    # ── New FK field ─────────────────────────────────────────────────────
    image = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='package_images',
        verbose_name='Image',
    )

    package_type = models.CharField(
        max_length=10,
        choices=PACKAGE_TYPE_CHOICES,
        default='non_room',
    )
    feature_group = models.ForeignKey(
        'features.FeatureGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='packages',
        help_text='Feature group whose features will be available as amenities in sub-packages.',
    )
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=205, blank=True)

    class Meta:
        ordering = ['position']

    @property
    def is_room(self):
        return self.package_type == 'room'

    @property
    def image_url(self):
        if self.image_id:
            try:
                return self.image.file.url
            except (ValueError, AttributeError):
                pass
        return None

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.id or self.position == 0:
                last_pos = Package.objects.select_for_update().aggregate(
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
        return f"{self.title} ({self.get_package_type_display()})"


class SubPackageAmenity(models.Model):
    """Through model for SubPackage.amenities — stores display order."""
    subpackage = models.ForeignKey('SubPackage', on_delete=models.CASCADE, related_name='amenity_links')
    feature = models.ForeignKey('features.Feature', on_delete=models.CASCADE, related_name='amenity_links')
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']
        unique_together = [('subpackage', 'feature')]

    def __str__(self):
        return f"{self.subpackage.title} — {self.feature.title} (pos {self.position})"


class SubPackage(MediaUsageMixin, models.Model):
    media_fields = ['image']
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='sub_packages')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = RichTextUploadingField(blank=True)


    # ── New FK field ─────────────────────────────────────────────────────
    image = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='subpackage_images',
        verbose_name='Image',
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Max guests")
    beds = models.PositiveIntegerField(null=True, blank=True)

    # Hall specific fields
    hall_size = models.CharField(max_length=255, null=True, blank=True)
    u_shape = models.CharField(max_length=255, null=True, blank=True)
    classroom = models.CharField(max_length=255, null=True, blank=True)
    theatre = models.CharField(max_length=255, null=True, blank=True)
    round_table = models.CharField(max_length=255, null=True, blank=True)

    amenities = models.ManyToManyField(
        'features.Feature',
        through=SubPackageAmenity,
        blank=True,
        related_name='subpackages',
    )

    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=205, blank=True)

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

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.id or self.position == 0:
                last_pos = SubPackage.objects.select_for_update().filter(
                    package=self.package
                ).aggregate(Max('position'))['position__max']
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
        return f"{self.title} → {self.package.title}"


class SubPackageImage(MediaUsageMixin, models.Model):
    media_fields = ['image']

    subpackage = models.ForeignKey(
        SubPackage,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Sub-Package'
    )
    image = models.ForeignKey(
        'media_manager.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subpackage_gallery_images'
    )
    title = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']
        verbose_name = 'Sub-Package Image'
        verbose_name_plural = 'Sub-Package Images'

    @property
    def image_url(self):
        """Return the file URL of the linked Media object, or None."""
        try:
            return self.image.file.url if self.image_id else None
        except (ValueError, AttributeError):
            return None

    def __str__(self):
        return self.title or f"Image for {self.subpackage.title}"