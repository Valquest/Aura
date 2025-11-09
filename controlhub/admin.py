from django.contrib import admin
from django import forms
from .models import User, Device, UserDeviceAccess, DeviceAction, Stat
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as DefaultUser


# Custom admin for DeviceAction
@admin.register(DeviceAction)
class DeviceActionAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'action_name', 'type_display', 'end_point', 'last_state')
    list_filter = ('type', 'last_state', 'device')
    search_fields = ('action_name', 'end_point', 'device__name')
    fields = ('device', 'action_name', 'type', 'end_point', 'last_state')

    def device_name(self, obj):
        return obj.device.name if obj.device else 'None'
    device_name.short_description = 'Device'

    def type_display(self, obj):
        return obj.get_type_display() if obj.type else 'None'
    type_display.short_description = 'Type'

# Unregister the default User model (if registered)
try:
    admin.site.unregister(DefaultUser)
except admin.sites.NotRegistered:
    pass

# Custom admin for User model
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'type_display', 'is_staff', 'is_active')
    list_filter = ('type', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'type', 'password1', 'password2'),
        }),
    )

    def type_display(self, obj):
        return obj.get_type_display() if obj.type else 'None'
    type_display.short_description = 'User Type'

admin.site.register(Stat)
admin.site.register(Device)
admin.site.register(UserDeviceAccess)