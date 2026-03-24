from django.contrib import admin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ('title', 'name', 'country', 'rating', 'via_type', 'active', 'position')
    list_filter   = ('active', 'rating', 'via_type')
    search_fields = ('title', 'name', 'country')
    ordering      = ('position',)