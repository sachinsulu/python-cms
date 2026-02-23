# core/models.py
from django.db import models


class Module(models.Model):
    label = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, help_text="Font Awesome class e.g. fa-solid fa-newspaper")
    url_name = models.CharField(max_length=100, help_text="Django URL name e.g. article_list")
    url_name_match = models.CharField(max_length=200, blank=True, help_text="Comma separated keywords to match active state")
    permission_app = models.CharField(max_length=100, blank=True, help_text="App label to check perms e.g. blog")
    superuser_only = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label