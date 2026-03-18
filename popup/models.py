from django.db import models


class Popup(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_CHOICES = [
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
    ]

    title      = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date   = models.DateField()
    type       = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_IMAGE)
    file       = models.FileField(upload_to='popups/', blank=True, null=True)
    link       = models.CharField(max_length=500, blank=True)
    status     = models.BooleanField(default=True)
    position   = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Popup'
        verbose_name_plural = 'Popups'

    def __str__(self):
        return self.title

    @property
    def is_image(self):
        return self.type == self.TYPE_IMAGE

    @property
    def is_video(self):
        return self.type == self.TYPE_VIDEO
