from django.contrib import admin
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display  = ('title', 'discount_type', 'start_date', 'end_date', 'active', 'position')
    list_filter   = ('discount_type', 'active')
    search_fields = ('title',)
    ordering      = ('position',)