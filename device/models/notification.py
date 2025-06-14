


from django.db import models
from .device import Device


# class Notification(models.Model):
#     device = models.ForeignKey(Device, on_delete=models.CASCADE)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Notif: {self.device} - {self.message}"




# device/models.py (Enhanced Notification model)
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('critical', 'Critical'),
        ('tamper', 'Tamper Alert'),
        ('low', 'Low Level'),
        ('medium', 'Medium Level'),
        ('high', 'High Level'),
        ('success', 'Success'),
        ('offline', 'Offline'),
        ('info', 'Information'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    title = models.CharField(max_length=200, default='Device Alert')
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='info',
        help_text="Type of alert for frontend styling"
    )
    alert = models.CharField(max_length=50, blank=True, default='')
    tamper = models.CharField(max_length=10, blank=True, default='')
    priority = models.IntegerField(
        default=50,
        help_text="Priority for sorting (100=critical, 1=lowest)"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.notification_type.upper()}: {self.device} - {self.title}"