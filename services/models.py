from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Service(models.Model):
    TYPE_MAIN_SERVICE = 'main-service'
    TYPE_SERVICE = 'service'
    TYPE_CHOICES = [
        (TYPE_MAIN_SERVICE, 'Main Service'),
        (TYPE_SERVICE, 'Service'),
    ]

    title    = models.CharField(max_length=255)
    image    = models.ImageField(upload_to='services/', blank=True, null=True)
    icon     = models.CharField(max_length=255, blank=True, help_text='CSS class e.g. fa-brands fa-instagram')
    link     = models.CharField(max_length=500, blank=True)
    content  = RichTextUploadingField(blank=True)
    status   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    type     = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_MAIN_SERVICE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title
