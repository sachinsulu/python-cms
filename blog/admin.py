from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'date', 'active', 'position']
    list_filter = ['active', 'date']
    search_fields = ['title', 'slug', 'author', 'content']
    prepopulated_fields = {'slug': ('title',)}
