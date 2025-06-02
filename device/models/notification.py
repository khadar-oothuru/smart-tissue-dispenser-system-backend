


from django.db import models
from .device import Device


# class Notification(models.Model):
#     device = models.ForeignKey(Device, on_delete=models.CASCADE)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Notif: {self.device} - {self.message}"




# device/models.py (add to Notification model)
class Notification(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    title = models.CharField(max_length=200, default='Device Alert')
    alert = models.CharField(max_length=50, blank=True)
    tamper = models.CharField(max_length=10, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.device} - {self.created_at}"