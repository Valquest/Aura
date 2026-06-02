from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as DefaultUser

from .models import Device, DeviceAction, DeviceToken, Stat, User, UserDeviceAccess


class DeviceTokenInline(admin.StackedInline):
    model = DeviceToken
    extra = 0
    readonly_fields = ('token', 'created_at', 'last_used')
    fields = ('token', 'created_at', 'last_used')

    def has_add_permission(self, request, obj=None):
        if obj and hasattr(obj, 'token'):
            return False
        return True


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'mac', 'ip', 'protocol', 'location', 'is_active', 'is_online_display', 'last_seen')
    list_filter = ('protocol', 'is_active')
    search_fields = ('name', 'mac', 'ip', 'location')
    inlines = [DeviceTokenInline]

    def is_online_display(self, obj):
        return obj.is_online
    is_online_display.boolean = True
    is_online_display.short_description = 'Online'


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
admin.site.register(UserDeviceAccess)
