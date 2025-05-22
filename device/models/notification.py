


from django.db import models
from .device import Device


class Notification(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif: {self.device} - {self.message}"


