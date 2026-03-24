from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

class CustomUserAdmin(DefaultUserAdmin):
    # Columns to display in the list view
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'active_status',  # Show Active/Inactive text
        'date_joined',
    )

    # Add filters in the sidebar
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    # Method to show "Active" or "Inactive" instead of a checkbox
    def active_status(self, obj):
        return "Active" if obj.is_active else "Inactive"
    active_status.short_description = 'Status'
    active_status.admin_order_field = 'is_active'

# Unregister the default UserAdmin
admin.site.unregister(User)

# Register the custom UserAdmin
admin.site.register(User, CustomUserAdmin)
