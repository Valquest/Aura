from .models import DeviceAction

def global_active_device_data(request):
    '''
    Passes global values about device action model
    '''
    active_devices = DeviceAction.objects.filter(last_state=True).count()

    return {
        'active_device_count': active_devices,
    }