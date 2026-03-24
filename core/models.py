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


class PageMeta(models.Model):
    """
    Stores SEO meta tags for list/section pages.
    Each row is linked to one Module via OneToOne.
    e.g. Module(url_name='faq_list') → PageMeta(meta_title='FAQ Page', ...)
    """
    module = models.OneToOneField(
        Module,
        on_delete=models.CASCADE,
        related_name='page_meta',
        help_text="The module/section this meta belongs to.",
    )
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Page title for search engines. Max 60 chars.",
    )
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        help_text="Page description for search engines. Max 160 chars.",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated keywords.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page Meta'
        verbose_name_plural = 'Page Meta'

    def __str__(self):
        return f"Meta → {self.module.label}"