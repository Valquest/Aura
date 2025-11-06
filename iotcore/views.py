import requests
import random
import time

from controlhub.models import DeviceAction
from django.http import JsonResponse
from django.shortcuts import HttpResponse

def toggle_device(request, action_id):
    """
    Simulated IoT device calls
    """
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Method not allowed, user POST.'},
            status=405
        )
    
    # Some delay
    time.sleep(3)

    random_num = random.randint(1, 9)

    # Case where IoT device is responsive
    if random_num >= 3:
        status = device_status_toggle(action_id)
        response_data = {
            'request_status': 'success',
            'device_action_status': status,
            'message': 'Device toggled successfully',
            'action_id': action_id,
            'random_value': random_num
        }

        return JsonResponse(response_data, status=200)
    # Case where IoT device is non-responsive
    else:
        last_device_status = DeviceAction.objects.get(id=action_id).last_state
        response_data = {
            'request_status': 'failure',
            'device_action_status': last_device_status,
            'message': 'Device toggled failed',
            'action_id': action_id,
            'random_value': random_num
        }
        return JsonResponse(response_data, status=400)

def device_status_toggle(action_id) -> bool:
    action = DeviceAction.objects.get(id=action_id)
    current_state = action.last_state
    if action.last_state != True:
        action.last_state = True
        action.save()
    else:
        action.last_state = False
        action.save()
    return action.last_state