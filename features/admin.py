from django.contrib import admin
from .models import Feature, FeatureGroup

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 0
    fields = ('title', 'icon', 'active', 'position')

@admin.register(FeatureGroup)
class FeatureGroupAdmin(admin.ModelAdmin):
    list_display  = ('title', 'active', 'position')
    list_filter   = ('active',)
    search_fields = ('title',)
    ordering      = ('position',)
    inlines       = [FeatureInline]

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display  = ('title', 'group', 'icon', 'active', 'position')
    list_filter   = ('active', 'group')
    search_fields = ('title', 'content', 'group__title')
    ordering      = ('group', 'position')