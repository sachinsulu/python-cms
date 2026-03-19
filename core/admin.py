from django.contrib import admin
from .models import Module, PageMeta

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['label', 'url_name', 'permission_app', 'superuser_only', 'is_active', 'order']
    list_editable = ['is_active', 'order']

@admin.register(PageMeta)
class PageMetaAdmin(admin.ModelAdmin):
    list_display = ['module', 'meta_title', 'updated_at']
    search_fields = ['module__label', 'meta_title']
    readonly_fields = ['updated_at']