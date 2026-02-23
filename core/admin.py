from django.contrib import admin
from .models import Module

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['label', 'url_name', 'permission_app', 'superuser_only', 'is_active', 'order']
    list_editable = ['is_active', 'order']