from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Package, SubPackage


class SubPackageInline(admin.TabularInline):
    model = SubPackage
    extra = 0
    fields = ('title', 'slug', 'price', 'capacity', 'beds', 'is_active', 'position')
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'package_type_display', 'sub_count', 'is_active_icon', 'position', 'created_at')
    list_display_links = ('title', 'slug')
    list_filter = ('is_active', 'package_type')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}
    inlines = [SubPackageInline]

    def package_type_display(self, obj):
        if obj.is_room:
            return mark_safe('<span style="color: #3b82f6;">🛏 Room</span>')
        return mark_safe('<span style="color: #8b5cf6;">📦 Non-Room</span>')
    package_type_display.short_description = "Type"

    def sub_count(self, obj):
        count = obj.sub_packages.count()
        return f"{count} item{'s' if count != 1 else ''}"
    sub_count.short_description = "Sub-Packages"

    def is_active_icon(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color: green;">✔</span>')
        return mark_safe('<span style="color: red;">✖</span>')
    is_active_icon.short_description = "Active"


@admin.register(SubPackage)
class SubPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'package', 'price', 'capacity', 'is_active', 'position')
    list_display_links = ('title',)
    list_filter = ('is_active', 'package')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}