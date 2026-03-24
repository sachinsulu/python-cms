from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Addresses', {
            'fields': ('fiscal_address', 'ktm_address'),
        }),
        ('Contact', {
            'fields': (
                'ktm_contact_info', 'ktm_email',
                'landline', 'phone', 'p_o_box',
                'email_address', 'whatsapp',
            ),
        }),
        ('Map & Content', {
            'fields': ('map_embed', 'content'),
        }),
        ('Meta', {
            'fields': ('updated_at',),
        }),
    )

    def has_add_permission(self, request):
        return not Location.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
