from django.contrib import admin
from .models import Gallery, GalleryImage

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'active', 'position')
    list_filter = ('type', 'active')
    search_fields = ('title',)
    inlines = [GalleryImageInline]
