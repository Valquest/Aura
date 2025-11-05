from django.urls import path
from . import views


urlpatterns = [
    path('toggle/<int:action_id>', views.toggle_device, 
        name='toggle_device')
]