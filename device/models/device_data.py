# device_data.py
from django.db import models
from .device import Device   # << Add this line
# other imports if needed

class DeviceData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    alert = models.CharField(max_length=20)
    count = models.IntegerField()
    refer_val = models.IntegerField()
    tamper = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.device} @ {self.timestamp}"
