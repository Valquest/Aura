from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Device(models.Model):
    mac = models.CharField(max_length=23)
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=4)
    model = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    last_seen = models.DateTimeField(auto_now=False)
    is_active = models.BooleanField(default=1)

    def __str__(self):
        return f"Device |{self.name}| was last seen on {self.last_seen}"

class Connection(models.Model):
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
        unique_together = ['outter_node', 'inner_node']

    def clean(self):
        if self.outter_node == self.inner_node:
            raise ValidationError("Connection must link distinct devices.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.outter_node} <-> {self.inner_node}"

class User(AbstractUser):
    """
    Standart user model with additional value for user type
    """
    # Defines account type in the system
    type = models.CharField(max_length=7) # admin, user, creator, guest

class Stat(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
