from django.db import models, transaction
from django.db.models import Max
from ckeditor_uploader.fields import RichTextUploadingField


class Offer(models.Model):
    DISCOUNT_NONE    = 'none'
    DISCOUNT_FIXED   = 'fixed'
    DISCOUNT_DYNAMIC = 'dynamic'
    DISCOUNT_MULTI   = 'multi'

    DISCOUNT_TYPE_CHOICES = [
        (DISCOUNT_NONE,    'None'),
        (DISCOUNT_FIXED,   'Fixed'),
        (DISCOUNT_DYNAMIC, 'Dynamic'),
        (DISCOUNT_MULTI,   'Multi'),
    ]

    title         = models.CharField(max_length=255)
    start_date    = models.DateField()
    end_date      = models.DateField()
    image         = models.ImageField(upload_to='offers/', blank=True, null=True)
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default=DISCOUNT_NONE,
    )

    # Fixed discount fields
    fixed_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fixed_rate     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fixed_people   = models.PositiveIntegerField(null=True, blank=True)

    # Dynamic / Multi tiers stored as JSON
    # Structure: [{"pax": 2, "rate": 100.00}, ...]
    tiers = models.JSONField(default=list, blank=True)

    link    = models.CharField(max_length=500, blank=True)
    content = RichTextUploadingField(blank=True)
    active  = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk or self.position == 0:
                last = Offer.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title