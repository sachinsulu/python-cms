from django.db import models, transaction
from django.utils.text import slugify
from django.db.models import Max


class Package(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('room', 'Room'),
        ('non_room', 'Non-Room'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='packages/', blank=True, null=True)
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

    class Meta:
        ordering = ['position']

    @property
    def is_room(self):
        return self.package_type == 'room'

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


class SubPackage(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='sub_packages')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='subpackages/', blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Max guests")
    beds = models.PositiveIntegerField(null=True, blank=True)

    amenities = models.ManyToManyField(
        'features.Feature',
        through=SubPackageAmenity,
        blank=True,
        related_name='subpackages',
    )

    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']

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