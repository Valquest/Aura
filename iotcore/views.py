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

    if random_num >= 3:
        device_status_toggle(action_id, True)
        response_data = {
            'status': 'success',
            'message': 'Device toggled successfully',
            'action_id': action_id,
            'random_value': random_num
        }

        return JsonResponse(response_data, status=200)
    else:
        device_status_toggle(action_id, False)
        response_data = {
            'status': 'failure',
            'message': 'Device toggled failed',
            'action_id': action_id,
            'random_value': random_num
        }
        return JsonResponse(response_data, status=400)

def device_status_toggle(action_id, status:bool) -> None:
    action = DeviceAction.objects.get(id=action_id)
    if action.last_state != status:
        action.last_state = status
        action.save()