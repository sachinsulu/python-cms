from django.contrib import admin
from django.utils.html import format_html
from .models import Media, MediaFolder


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "created_at"]
    list_filter = ["parent"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ["title", "preview_thumb", "folder", "type", "size_display", "uploaded_by", "created_at"]
    list_filter = ["type", "folder"]
    search_fields = ["title", "alt_text"]
    readonly_fields = ["type", "size", "width", "height", "created_at", "preview_thumb"]
    ordering = ["-created_at"]

    def preview_thumb(self, obj):
        if obj.is_image and obj.file:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:80px; object-fit:cover; border-radius:3px;" />',
                obj.file.url,
            )
        return "—"
    preview_thumb.short_description = "Preview"

    def size_display(self, obj):
        return obj.size_display
    size_display.short_description = "Size"