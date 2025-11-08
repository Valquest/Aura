from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Device(models.Model):
    """
    Stores device information MCU (Microcontroller Unit) information
    """
    mac = models.CharField(max_length=23)
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=4, null=True, blank=True)
    model = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    ip = models.GenericIPAddressField(null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=False, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Device | {self.name} | was last seen on {self.last_seen}"

class Connection(models.Model):
    """
    Stores MCU (Microcontroller Unit) connection data. Which MCU connects to
    which MCU
    """
    outter_node = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='outter_node',
        help_text="Node which is closer to the server"
    )
    inner_node = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='inner_node',
        help_text="Node which is further from the server"
    )

    class Meta:
        # Make sure there are no doublicate row entries for node columns
        unique_together = ['outter_node', 'inner_node']

    # Additional check before adding new entries to see if nodes are not
    # pointed at themselves
    def clean(self):
        if self.outter_node == self.inner_node:
            raise ValidationError("Connection must link distinct devices.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.outter_node} <-> {self.inner_node}"

class DeviceAction(models.Model):
    """
    This model handles http endpoints and action that was called state
    """

    TYPE_CHOICES = (
        ('button','Button'),
        ('sensor','Sensor'),
    )

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    end_point = models.CharField(max_length=64)
    action_name = models.CharField(max_length=64)
    type = models.CharField(max_length=6, null=True, choices=TYPE_CHOICES)
    stat = models.ForeignKey('Stat', on_delete=models.SET_NULL, null=True, blank=True, related_name='stat_for_action')
    last_state = models.BooleanField(default=False)

class User(AbstractUser):
    """
    Standart user model with additional value for user type
    """

    TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('creator', 'Creator'),
        ('guest', 'Guest'),
    )

    # Defines account type in the system
    type = models.CharField(max_length=7, choices=TYPE_CHOICES) # admin, user, creator, guest

class UserDeviceAccess(models.Model):
    """
    Stores information about users privileges in regards to IoT networks
    node access (Which nodes user can access)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

class Stat(models.Model):
    """
    Stores measurements done by MCU (Microcontroller Unit) if MCU outputs
    data
    """
    action = models.ForeignKey(DeviceAction, on_delete=models.CASCADE, null=True, related_name='action_for_stat')
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(null=True, blank=True)

    def clean(self):
        if self.action and self.action.type != 'sensor':
            raise ValidationError({
                'action': "Stat can only be created for a DeviceAction with type 'sensor'."
            })
            super().clean()