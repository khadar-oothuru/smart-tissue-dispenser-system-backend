
from django.db import models
from django.conf import settings

class Device(models.Model):
    name = models.CharField(max_length=100)
    floor_number = models.IntegerField()
    room_number = models.CharField(max_length=50)
    device_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True, db_index=True,
        help_text="Optional unique device ID from ESP32"
    )
    
    # Add these two fields only
    registration_type = models.CharField(
        max_length=20, 
        choices=[('manual', 'Manual'), ('wifi', 'WiFi')],
        default='manual'
    )
    metadata = models.JSONField(default=dict, blank=True, null=True)  # Store WiFi-specific data
    
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Room {self.room_number}"