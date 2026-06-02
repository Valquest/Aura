import secrets

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Device(models.Model):
    """
    Stores device information MCU (Microcontroller Unit) information
    """
    PROTOCOL_CHOICES = [('http', 'HTTP'), ('mqtt', 'MQTT')]

    mac = models.CharField(max_length=23)
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=4, null=True, blank=True)
    model = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    ip = models.GenericIPAddressField(null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=False, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    protocol = models.CharField(max_length=8, choices=PROTOCOL_CHOICES, default='http')
    heartbeat_interval = models.PositiveIntegerField(
        default=60,
        help_text="Expected heartbeat interval in seconds. Used to determine online/offline status."
    )

    @property
    def is_online(self) -> bool:
        if not self.last_seen:
            return False
        threshold = timezone.now() - timezone.timedelta(seconds=self.heartbeat_interval * 2.5)
        return self.last_seen >= threshold

    def __str__(self):
        return f"Device name: {self.name}"

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
    last_state = models.BooleanField(default=False)

    def __str__(self):
        return f'Action name: {self.action_name} | type: {self.type}'

class DeviceToken(models.Model):
    """
    Per-device API token. Devices include this in X-Aura-Token header for authentication.
    """
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='token')
    token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token for {self.device.name}"


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
    device_action = models.ForeignKey(DeviceAction, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(null=True, blank=True)