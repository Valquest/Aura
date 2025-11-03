from django.contrib import admin
from .models import User, Device, UserDeviceAccess
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as DefaultUser

# Register your models here.

admin.site.register(Device)
admin.site.register(UserDeviceAccess)

# Unregister the default User model (if registered)
try:
    admin.site.unregister(DefaultUser)
except admin.sites.NotRegistered:
    pass

# Define a custom admin class for your User model
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Customize fields to display in the admin list view
    list_display = ('username', 'email', 'type', 'is_staff', 'is_active')
    # Add search functionality
    search_fields = ('username', 'email', 'type')
    # Add filters in the sidebar
    list_filter = ('type', 'is_staff', 'is_active')
    # Define fields to show in the edit form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Fields for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'type', 'password1', 'password2'),
        }),
    )
