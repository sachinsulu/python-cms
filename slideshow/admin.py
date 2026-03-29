from django.contrib import admin
from .models import Slideshow


@admin.register(Slideshow)
class SlideshowAdmin(admin.ModelAdmin):
    list_display  = ('title', 'type', 'active', 'position')
    list_filter   = ('type', 'active')
    search_fields = ('title', 'subtitle')
    ordering      = ('position',)