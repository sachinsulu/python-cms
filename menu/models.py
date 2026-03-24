from django.db import models, transaction
from django.db.models import Max


class MenuItem(models.Model):
    """
    Represents a single navigation item in the website header menu.
    Supports one level of dropdown children via a self-referential FK.

    Examples:
        Home           → label="Home",  url="/",           parent=None
        About Us       → label="About", url="/about/",     parent=None
          ↳ Our Team   → label="Team",  url="/about/team/",parent=<About>
    """

    label = models.CharField(
        max_length=100,
        help_text="Display text shown in the menu, e.g. 'About Us'"
    )
    url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Link URL. Use relative paths e.g. /about/ or full URLs https://..."
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="Leave blank for a top-level item. Select a parent to make this a dropdown child."
    )
    open_in_new_tab = models.BooleanField(
        default=False,
        help_text="Open this link in a new browser tab (target='_blank')"
    )
    active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            is_new = self.pk is None
            parent_changed = False

            if not is_new:
                old = MenuItem.objects.filter(pk=self.pk).values_list('parent_id', flat=True).first()
                if old != self.parent_id:
                    parent_changed = True

            if is_new or parent_changed:
                siblings = MenuItem.objects.select_for_update().filter(
                    parent=self.parent
                )
                if not is_new:
                    siblings = siblings.exclude(pk=self.pk)
                last_pos = siblings.aggregate(
                    Max('position')
                )['position__max']
                self.position = (last_pos or 0) + 1

            super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"  ↳ {self.label} (under {self.parent.label})"
        return self.label

    @property
    def is_dropdown(self):
        """True if this top-level item has active children (i.e. it's a dropdown)."""
        return self.children.filter(active=True).exists()

    @property
    def target(self):
        return '_blank' if self.open_in_new_tab else '_self'