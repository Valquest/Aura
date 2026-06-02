from django.urls import path
from . import views

urlpatterns = [
    path('toggle/<int:action_id>', views.toggle_device, name='toggle_device'),
    path('ingest/<int:action_id>/', views.ingest_sensor_data, name='ingest_sensor_data'),
    path('heartbeat/<int:device_id>/', views.device_heartbeat, name='device_heartbeat'),
    path('events/', views.sse_stream, name='sse_stream'),
]
