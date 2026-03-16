from django.contrib import admin
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display  = ('title', 'content', 'active', 'position')
    list_filter   = ('active',)
    search_fields = ('title', 'content')
    ordering      = ('position',)

    def answer_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    answer_preview.short_description = 'Answer'
