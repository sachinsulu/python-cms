from django.db import models


class Social(models.Model):
    TYPE_SOCIAL = 'social'
    TYPE_OTA = 'ota'
    TYPE_CHOICES = [
        (TYPE_SOCIAL, 'Social'),
        (TYPE_OTA, 'OTA'),
    ]

    title    = models.CharField(max_length=255)
    link     = models.CharField(max_length=500, blank=True)
    image    = models.ImageField(upload_to='social/', blank=True, null=True)
    icon     = models.CharField(max_length=255, blank=True, help_text='CSS class e.g. fa-brands fa-instagram')
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    type     = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_SOCIAL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Social / OTA'
        verbose_name_plural = 'Socials / OTAs'

    def __str__(self):
        return self.title