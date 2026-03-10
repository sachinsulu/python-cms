from django.contrib import admin
from django.utils.html import format_html
from .models import MenuItem


class ChildMenuItemInline(admin.TabularInline):
    model = MenuItem
    fk_name = 'parent'
    extra = 0
    fields = ('label', 'url', 'open_in_new_tab', 'active', 'position')
    verbose_name = "Dropdown Child"
    verbose_name_plural = "Dropdown Children"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'parent', 'open_in_new_tab', 'active_icon', 'position')
    list_display_links = ('label',)
    list_filter = ('active', 'parent')
    search_fields = ('label', 'url')
    ordering = ('parent', 'position')
    inlines = [ChildMenuItemInline]

    def get_queryset(self, request):
        # Only show top-level items in the list (children shown via inline)
        return super().get_queryset(request).filter(parent=None)

    def active_icon(self, obj):
        if obj.active:
            return format_html('<span style="color: green;">✔</span>')
        return format_html('<span style="color: red;">✖</span>')
    active_icon.short_description = "Active"