import json
import queue
import threading
from functools import wraps

import requests as http_client
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from controlhub.models import Connection, Device, DeviceAction, DeviceToken, Stat

# ─── SSE broadcast ──────────────────────────────────────────────────────────

_sse_listeners: list = []
_sse_lock = threading.Lock()


def broadcast_sse(data: dict):
    with _sse_lock:
        for q in list(_sse_listeners):
            q.put(data)


@login_required
def sse_stream(request):
    def event_stream():
        q = queue.Queue()
        with _sse_lock:
            _sse_listeners.append(q)
        try:
            while True:
                try:
                    data = q.get(timeout=30)
                    yield f"data: {json.dumps(data)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            with _sse_lock:
                if q in _sse_listeners:
                    _sse_listeners.remove(q)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


# ─── Device token auth ───────────────────────────────────────────────────────

def _get_device_by_token(token_value: str):
    try:
        token_obj = DeviceToken.objects.select_related('device').get(token=token_value)
        token_obj.last_used = timezone.now()
        token_obj.save(update_fields=['last_used'])
        return token_obj.device
    except DeviceToken.DoesNotExist:
        return None


def require_device_token(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token_value = request.headers.get('X-Aura-Token')
        if not token_value:
            return JsonResponse({'error': 'Missing device token.'}, status=401)
        device = _get_device_by_token(token_value)
        if device is None:
            return JsonResponse({'error': 'Invalid device token.'}, status=403)
        request.iot_device = device
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Command delivery ────────────────────────────────────────────────────────

def _get_reachable_node(device):
    """Walk Connection chain to find the outermost node with a known IP."""
    if device.ip:
        return device, []
    try:
        conn = Connection.objects.select_related('outter_node').get(inner_node=device)
        outer, path = _get_reachable_node(conn.outter_node)
        return outer, path + [device]
    except Connection.DoesNotExist:
        return None, []


def _call_device(reachable, action, relay_target_mac=None) -> bool:
    url = f"http://{reachable.ip}/{action.end_point}"
    token = getattr(reachable, 'token', None)
    headers = {}
    if token:
        headers['X-Aura-Token'] = token.token
    if relay_target_mac:
        headers['X-Aura-Relay-Target'] = relay_target_mac
    try:
        resp = http_client.post(url, headers=headers, timeout=4)
        return resp.ok
    except http_client.RequestException:
        return False


# ─── Views ───────────────────────────────────────────────────────────────────

@login_required
def toggle_device(request, action_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed, use POST.'}, status=405)

    action = get_object_or_404(DeviceAction, id=action_id)
    device = action.device

    # No IP configured — simulate (useful during development without real hardware)
    if not device.ip:
        action.last_state = not action.last_state
        action.save(update_fields=['last_state'])
        active_count = DeviceAction.objects.filter(last_state=True).count()
        broadcast_sse({'type': 'active_count', 'count': active_count})
        return JsonResponse({
            'request_status': 'success',
            'device_action_status': action.last_state,
            'message': 'Simulated toggle (no device IP configured).',
            'action_id': action_id,
        }, status=200)

    reachable, relay_path = _get_reachable_node(device)

    if reachable is None:
        return JsonResponse({
            'request_status': 'failure',
            'device_action_status': action.last_state,
            'message': 'Device has no IP and no reachable relay node.',
            'action_id': action_id,
        }, status=503)

    relay_mac = device.mac if relay_path else None
    success = _call_device(reachable, action, relay_target_mac=relay_mac)

    if success:
        action.last_state = not action.last_state
        action.save(update_fields=['last_state'])
        active_count = DeviceAction.objects.filter(last_state=True).count()
        broadcast_sse({'type': 'active_count', 'count': active_count})
        return JsonResponse({
            'request_status': 'success',
            'device_action_status': action.last_state,
            'message': 'Device toggled successfully.',
            'action_id': action_id,
        }, status=200)

    return JsonResponse({
        'request_status': 'failure',
        'device_action_status': action.last_state,
        'message': 'Device did not respond.',
        'action_id': action_id,
    }, status=400)


@csrf_exempt
@require_device_token
def ingest_sensor_data(request, action_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed, use POST.'}, status=405)

    action = get_object_or_404(DeviceAction, id=action_id)

    if action.device != request.iot_device:
        return JsonResponse({'error': 'Token does not own this action.'}, status=403)

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    stat = Stat.objects.create(device_action=action, data=payload)

    device = request.iot_device
    device.last_seen = timezone.now()
    device.save(update_fields=['last_seen'])

    broadcast_sse({
        'type': 'stat',
        'action_id': action_id,
        'data': payload,
        'timestamp': stat.timestamp.isoformat(),
    })

    return JsonResponse({'status': 'ok'})


@csrf_exempt
@require_device_token
def device_heartbeat(request, device_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed, use POST.'}, status=405)

    device = get_object_or_404(Device, id=device_id)

    if device != request.iot_device:
        return JsonResponse({'error': 'Token does not match device.'}, status=403)

    update_fields = ['last_seen']
    device.last_seen = timezone.now()

    try:
        body = json.loads(request.body) if request.body else {}
        if 'ip' in body:
            device.ip = body['ip']
            update_fields.append('ip')
    except (json.JSONDecodeError, ValueError):
        pass

    device.save(update_fields=update_fields)

    broadcast_sse({
        'type': 'heartbeat',
        'device_id': device_id,
        'online': True,
    })

    return JsonResponse({'status': 'ok'})
