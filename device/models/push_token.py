


from django.db import models
from django.conf import settings



class ExpoPushToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)

    def __str__(self):
        return f"PushToken: {self.user.username}"