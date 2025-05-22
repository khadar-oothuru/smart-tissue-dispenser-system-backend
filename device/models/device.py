# myapp/models/device.py
from django.db import models
from django.conf import settings

class Device(models.Model):
    name = models.CharField(max_length=100)
    floor_number = models.IntegerField()
    room_number = models.CharField(max_length=50)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Device {self.id} - Room {self.room_number}"
