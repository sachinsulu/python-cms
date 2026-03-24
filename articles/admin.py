from django.contrib import admin
from django.utils.html import format_html
from .models import Article
from django.utils.safestring import mark_safe

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # Fields to show in the list view
    list_display = (
        'title',
        'slug',
        'homepage_icon',
        'active_icon',
        'image_thumb',
        'created_at',
        'updated_at'
    )
    fieldsets = (
        ("Main Content", {
            "fields": ("title", "subtitle", "slug", "content", "image", "author")
        }),
        ("SEO Meta Data (Database)", {
            "classes": ("collapse",),  # This makes the section toggleable
            "fields": ("meta_title", "meta_description", "meta_keywords"),
            "description": "These fields are saved in the DB and used for frontend <meta> tags."
        }),
        ("Display Settings", {
            "fields": ("homepage", "active", "position")
        }),
    )
    
    # Make fields clickable
    list_display_links = ('title', 'slug')
    
    # Filters on the right sidebar
    list_filter = ('homepage', 'active', 'created_at')
    
    # Searchable fields
    search_fields = ('title', 'subtitle', 'content')
    
    # Auto-generate slug from title
    prepopulated_fields = {"slug": ("title",)}
    
    # Readonly fields in admin form
    readonly_fields = ('image_thumb',)
    
    # Function to show image thumbnail
    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="object-fit: cover;"/>', obj.image.url)
        return "-"
    image_thumb.short_description = "Image"
    
    # Show homepage flag as icon
    def homepage_icon(self, obj):
        if obj.homepage:
            return mark_safe('<span style="color: green;">✔</span>')
        return mark_safe('<span style="color: red;">✖</span>')

    def active_icon(self, obj):
        if obj.active:
            return mark_safe('<span style="color: green;">✔</span>')
        return mark_safe('<span style="color: red;">✖</span>')
