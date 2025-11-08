# your_app/admin.py
from django.contrib import admin
from django import forms
from .models import User, Device, UserDeviceAccess, DeviceAction, Stat
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as DefaultUser

# Custom form for Stat to filter action and device dropdowns
class StatAdminForm(forms.ModelForm):
    class Meta:
        model = Stat
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter action dropdown to only DeviceActions with type='sensor'
        self.fields['action'].queryset = DeviceAction.objects.filter(type='sensor')
        # Filter device dropdown to only Devices with at least one DeviceAction of type='sensor'
        self.fields['device'].queryset = Device.objects.filter(deviceaction__type='sensor').distinct()
        print("StatAdminForm action queryset:", self.fields['action'].queryset.values('id', 'action_name', 'type'))
        print("StatAdminForm device queryset:", self.fields['device'].queryset.values('id', 'name'))

# Custom admin for Device
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'mac', 'location', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'mac', 'location')

# Custom admin for DeviceAction
@admin.register(DeviceAction)
class DeviceActionAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'action_name', 'type_display', 'end_point', 'stat_name', 'last_state')
    list_filter = ('type', 'last_state', 'device')
    search_fields = ('action_name', 'end_point', 'device__name', 'stat__id')
    autocomplete_fields = ['device', 'stat']
    fields = ('device', 'action_name', 'type', 'end_point', 'stat', 'last_state')

    def device_name(self, obj):
        return obj.device.name if obj.device else 'None'
    device_name.short_description = 'Device'

    def stat_name(self, obj):
        return obj.stat.id if obj.stat else 'None'
    stat_name.short_description = 'Stat'

    def type_display(self, obj):
        return obj.get_type_display() if obj.type else 'None'
    type_display.short_description = 'Type'

# Custom admin for Stat
@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    form = StatAdminForm
    list_display = ('device_name', 'action_name', 'timestamp', 'data')
    list_filter = ('timestamp', 'device')
    search_fields = ('device__name', 'action__action_name')
    fields = ('device', 'action', 'data')

    def device_name(self, obj):
        return obj.device.name if obj.device else 'None'
    device_name.short_description = 'Device'

    def action_name(self, obj):
        return obj.action.action_name if obj.action else 'None'
    action_name.short_description = 'Action'

# Custom admin for UserDeviceAccess
@admin.register(UserDeviceAccess)
class UserDeviceAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'device')
    list_filter = ('user', 'device')
    search_fields = ('user__username', 'device__name')

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