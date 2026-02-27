from django.contrib import admin
from .models import Social


@admin.register(Social)
class SocialAdmin(admin.ModelAdmin):
    list_display  = ('title', 'type', 'link', 'active', 'position')
    list_filter   = ('type', 'active')
    search_fields = ('title',)
    ordering      = ('type', 'position')