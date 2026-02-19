from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'package_type_display', 'is_active_icon', 'image_thumb', 'position', 'created_at')
    list_display_links = ('title', 'slug')
    list_filter = ('is_active', 'package_type')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}

    def package_type_display(self, obj):
        if obj.is_room:
            return mark_safe('<span style="color: #3b82f6;">🛏 Room</span>')
        return mark_safe('<span style="color: #8b5cf6;">📦 Non-Room</span>')
    package_type_display.short_description = "Type"

    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="object-fit: cover;"/>', obj.image.url)
        return "-"
    image_thumb.short_description = "Image"

    def is_active_icon(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color: green;">✔</span>')
        return mark_safe('<span style="color: red;">✖</span>')
    is_active_icon.short_description = "Active"