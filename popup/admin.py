from django.contrib import admin
from .models import Popup


@admin.register(Popup)
class PopupAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'start_date', 'end_date', 'status', 'position')
    list_filter  = ('type', 'status')
    search_fields = ('title',)
    ordering = ('position',)
