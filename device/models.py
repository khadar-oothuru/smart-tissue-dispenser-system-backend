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

class DeviceData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    alert = models.CharField(max_length=20)
    count = models.IntegerField()
    refer_val = models.IntegerField()
    tamper = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.device} @ {self.timestamp}"

class Notification(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif: {self.device} - {self.message}"
