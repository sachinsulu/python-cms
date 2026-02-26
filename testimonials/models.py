from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Testimonial(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    title    = models.CharField(max_length=255)
    name     = models.CharField(max_length=255)
    content  = RichTextUploadingField()
    rating   = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    image    = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    linksrc  = models.URLField(blank=True, null=True, verbose_name='Link Source')
    country  = models.CharField(max_length=100, blank=True)
    via_type = models.CharField(max_length=100, blank=True, verbose_name='Via')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return self.title