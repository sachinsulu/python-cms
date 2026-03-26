# media_manager/admin.py
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Media, MediaFolder


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display  = ["name", "parent", "media_count", "created_at"]
    list_filter   = ["parent"]
    search_fields = ["name"]
    ordering      = ["name"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _media_count=Count("media", distinct=True)
        )

    def media_count(self, obj):
        return obj._media_count
    media_count.short_description = "Files"
    media_count.admin_order_field = "_media_count"


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display   = [
        "preview_thumb", "title", "folder", "type", "size_display",
        "alt_status", "active", "usage_count", "uploaded_by", "created_at",
    ]
    list_filter    = ["active", "type", "folder", "created_at"]
    search_fields  = ["title", "alt_text"]
    readonly_fields = [
        "type", "size", "width", "height", "created_at",
        "preview_thumb", "usage_list",
    ]
    ordering       = ["-created_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _usage_count=Count("usages", distinct=True)
        )

    def preview_thumb(self, obj):
        if obj.is_image and obj.file:
            return format_html(
                '<img src="{}" style="max-height:50px;max-width:80px;'
                'object-fit:cover;border-radius:3px;" />',
                obj.file.url,
            )
        return "—"
    preview_thumb.short_description = "Preview"

    def size_display(self, obj):
        return obj.size_display
    size_display.short_description = "Size"

    def alt_status(self, obj):
        if obj.alt_text:
            return format_html('<span style="color:green;">✔</span>')
        return mark_safe('<span style="color:red;" title="Missing alt text">✖</span>')
    alt_status.short_description = "Alt"

    def usage_count(self, obj):
        count = obj._usage_count
        color = "#dc2626" if count == 0 else "#16a34a"
        return format_html('<span style="color:{};">{}</span>', color, count)
    usage_count.short_description = "Uses"
    usage_count.admin_order_field = "_usage_count"

    def usage_list(self, obj):
        usages = obj.usages.select_related("content_type").all()
        if not usages:
            return "Not used anywhere."
        items = "".join(
            f"<li>{u.content_type.app_label}.{u.content_type.model} "
            f"#{u.object_id} ({u.field_name})</li>"
            for u in usages
        )
        return format_html("<ul>{}</ul>", format_html(items))
    usage_list.short_description = "Used in"
